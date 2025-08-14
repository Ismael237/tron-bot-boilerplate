
from decimal import Decimal, InvalidOperation
from typing import Dict

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from database.database import SessionLocal
from database.models import (
    User,
    Withdrawal,
    WithdrawalStatus,
    Transaction,
    TransactionType,
    TransactionStatus,
)
from bot.keyboards import (
    MAIN_MENU_BTN,
    withdraw_reply_keyboard,
    withdrawal_confirm_inline_keyboard,
    main_reply_keyboard,
    cancel_withdraw_keyboard,
)
from bot.messages import (
    msg_withdraw_start,
    msg_invalid_amount,
    msg_amount_out_of_bounds,
    msg_insufficient_balance,
    msg_ask_address,
    msg_invalid_address,
    msg_confirm_withdraw,
    msg_daily_limit_exceeded,
    msg_withdraw_submitted,
    msg_withdraw_cancelled,
    msg_session_expired,
)
from bot.utils import escape_markdown_v2, format_trx_escaped, format_trx
from utils.helpers import get_utc_date, get_utc_time
from utils.validators import is_valid_tron_address
from config import DAILY_WITHDRAWAL_LIMIT, MIN_WITHDRAWAL_AMOUNT, WITHDRAWAL_FEE_RATE


# ==============================
# Local state helpers
# ==============================

def _withdraw_state(context: ContextTypes.DEFAULT_TYPE) -> Dict:
    return context.user_data.setdefault("withdraw", {})


def _reset_state(context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("withdraw", None)


# ==============================
# Entry point
# ==============================
async def handle_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = SessionLocal()
    try:
        telegram_id = str(update.effective_user.id)
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            await update.message.reply_markdown_v2("❌ *You are not registered\.* Use /start to register\.")
            return

        _reset_state(context)
        state = _withdraw_state(context)
        state["step"] = "amount"

        balance_trx = format_trx(user.account_balance)
        min_trx = format_trx(MIN_WITHDRAWAL_AMOUNT)
        max_trx = format_trx(DAILY_WITHDRAWAL_LIMIT)

        await update.message.reply_markdown_v2(
            msg_withdraw_start(balance_trx, min_trx, max_trx, MAIN_MENU_BTN),
            reply_markup=withdraw_reply_keyboard(),
        )
    finally:
        session.close()


# ==============================
# Text message handler
# ==============================
async def process_withdraw_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "withdraw" not in context.user_data:
        return

    state = _withdraw_state(context)
    step = state.get("step")

    if step == "amount":
        await _handle_amount_input(update, context, state)
    elif step == "address":
        await _handle_address_input(update, context, state)


async def _handle_amount_input(update: Update, context: ContextTypes.DEFAULT_TYPE, state: Dict):
    raw = update.message.text.strip().replace(" TRX", "").replace(",", "")
    try:
        amount = Decimal(raw)
    except InvalidOperation:
        await update.message.reply_markdown_v2(msg_invalid_amount())
        return

    if amount < Decimal(str(MIN_WITHDRAWAL_AMOUNT)) or amount > Decimal(str(DAILY_WITHDRAWAL_LIMIT)):
        await update.message.reply_markdown_v2(
            msg_amount_out_of_bounds(format_trx(MIN_WITHDRAWAL_AMOUNT), format_trx(DAILY_WITHDRAWAL_LIMIT))
        )
        return

    session = SessionLocal()
    try:
        user = session.query(User).filter_by(telegram_id=str(update.effective_user.id)).first()
        if not user or Decimal(user.account_balance) < amount:
            await update.message.reply_markdown_v2(msg_insufficient_balance())
            return
    finally:
        session.close()

    state["amount"] = amount
    state["step"] = "address"

    fee = (amount * Decimal(str(WITHDRAWAL_FEE_RATE))).quantize(Decimal("0.01"))
    net = amount - fee

    await update.message.reply_markdown_v2(
        msg_ask_address(format_trx(amount), format_trx(net), f"{int(WITHDRAWAL_FEE_RATE * 100)}%"),
        reply_markup=cancel_withdraw_keyboard(),
    )


async def _handle_address_input(update: Update, context: ContextTypes.DEFAULT_TYPE, state: Dict):
    address = update.message.text.strip()
    if not is_valid_tron_address(address):
        await update.message.reply_markdown_v2(msg_invalid_address())
        return

    state["address"] = escape_markdown_v2(address)
    state["step"] = "confirm"
    amount = state["amount"]

    await update.message.reply_markdown_v2(
        msg_confirm_withdraw(format_trx(amount), address),
        reply_markup=withdrawal_confirm_inline_keyboard(amount),
    )


# ==============================
# Callback query handlers
# ==============================
async def confirm_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    state = _withdraw_state(context)
    if state.get("step") != "confirm":
        await query.edit_message_text(msg_session_expired(), parse_mode=ParseMode.MARKDOWN_V2)
        _reset_state(context)
        await query.message.reply_markdown_v2(MAIN_MENU_BTN, reply_markup=main_reply_keyboard())
        return

    amount = state.get("amount")
    address = state.get("address")

    session = SessionLocal()
    try:
        user = session.query(User).filter_by(telegram_id=str(query.from_user.id)).first()
        if not user or Decimal(user.account_balance) < amount:
            await query.edit_message_text(msg_insufficient_balance(), parse_mode=ParseMode.MARKDOWN_V2)
            _reset_state(context)
            await query.message.reply_markdown_v2(MAIN_MENU_BTN, reply_markup=main_reply_keyboard())
            return

        # Check daily withdrawal limit
        today = get_utc_date()
        daily_withdrawals = session.query(Withdrawal).filter(
            Withdrawal.user_id == user.id,
            Withdrawal.status != WithdrawalStatus.failed,
            Withdrawal.created_at >= today,
        ).all()
        total_daily_withdrawn = sum(w.amount_trx for w in daily_withdrawals)
        remaining_limit = Decimal(str(DAILY_WITHDRAWAL_LIMIT)) - Decimal(str(total_daily_withdrawn))

        if amount > remaining_limit:
            await query.edit_message_text(
                msg_daily_limit_exceeded(
                    format_trx(DAILY_WITHDRAWAL_LIMIT),
                    format_trx(total_daily_withdrawn),
                    format_trx(remaining_limit),
                    format_trx(amount),
                ),
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            _reset_state(context)
            await query.message.reply_markdown_v2(MAIN_MENU_BTN, reply_markup=main_reply_keyboard())
            return

        # Debit & record
        withdrawal = Withdrawal(
            user_id=user.id,
            amount_trx=amount,
            to_address=address,
            status=WithdrawalStatus.pending,
            created_at=get_utc_time(),
        )
        session.add(withdrawal)
        session.commit()

        tx = Transaction(
            user_id=user.id,
            type=TransactionType.withdrawal,
            amount=amount,
            status=TransactionStatus.pending,
            description="User initiated withdrawal",
            reference_id=str(withdrawal.id),
            created_at=get_utc_time(),
        )
        session.add(tx)
        session.commit()

        msg = msg_withdraw_submitted(format_trx(amount), format_trx(remaining_limit - amount))
        await query.edit_message_text(msg, parse_mode=ParseMode.MARKDOWN_V2)
    finally:
        session.close()

    _reset_state(context)
    await query.message.reply_markdown_v2(MAIN_MENU_BTN, reply_markup=main_reply_keyboard())


async def cancel_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        _reset_state(context)
        await update.message.reply_markdown_v2(msg_withdraw_cancelled(), reply_markup=main_reply_keyboard())
        await update.message.reply_markdown_v2(MAIN_MENU_BTN, reply_markup=main_reply_keyboard())
        return

    await query.answer()
    _reset_state(context)
    await query.edit_message_text(msg_withdraw_cancelled(), parse_mode=ParseMode.MARKDOWN_V2)
    await query.message.reply_markdown_v2(MAIN_MENU_BTN, reply_markup=main_reply_keyboard())
