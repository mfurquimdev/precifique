//! Lexer for the precifique inventory format.
//!
//! This module wires the ALEX-generated DFA tables (`lexer_data`) to a
//! hand-written [`PrecifiqueLexerDriver`] that converts raw byte matches into
//! typed [`PrecifiqueToken`]s.
//!
//! Mode transitions (managed by [`PrecifiqueLexerDriver::action`]):
//!
//! ```text
//!  Initial ──Header──►  AfterHeader ──HeaderNl──► Initial
//!          ──Indent──►  Indented
//!                           ├──QtyAt────► Price ──PriceNl──► Initial
//!                           └──QtyTimes─► CompName ──CompNameNl──► Initial
//! ```

use crate::token::{PrecifiqueToken, TokenID, TokenValue};
use parlex::{Lexer, LexerDriver, LexerStats, ParlexError};
use std::marker::PhantomData;
use try_next::TryNextWithContext;

/// Includes the ALEX-generated DFA tables and mode/rule enums.
pub mod lexer_data {
    include!(concat!(env!("OUT_DIR"), "/lexer_data.rs"));
}

use lexer_data::{LexData, Mode, Rule};

// ─── Driver ──────────────────────────────────────────────────────────────────

/// Stateless driver: handles every ALEX rule match and emits `PrecifiqueToken`s.
pub struct PrecifiqueLexerDriver<I> {
    _marker: PhantomData<I>,
}

impl<I> LexerDriver for PrecifiqueLexerDriver<I>
where
    I: TryNextWithContext<(), Item = u8, Error: std::fmt::Display + 'static>,
{
    type LexerData = LexData;
    type Token = PrecifiqueToken;
    type Lexer = Lexer<I, Self, ()>;
    type Context = ();

    fn action(
        &mut self,
        lexer: &mut Self::Lexer,
        _context: &mut (),
        rule: Rule,
    ) -> Result<(), ParlexError> {
        match rule {
            // ── Initial mode ────────────────────────────────────────────────
            Rule::BlankLine => {
                // blank line — skip, stay in Initial
            }

            Rule::Header => {
                // Full name line (no leading whitespace).
                // Trim trailing whitespace before storing.
                let text = lexer.take_str()?;
                let name = text.trim().to_owned();
                lexer.yield_token(PrecifiqueToken {
                    token_id: TokenID::Name,
                    span: Some(lexer.span()),
                    value: TokenValue::Name(name),
                });
                lexer.begin(Mode::AfterHeader);
            }

            Rule::Indent => {
                // 4-space indent — emit Indent, enter Indented mode.
                lexer.yield_token(PrecifiqueToken {
                    token_id: TokenID::Indent,
                    span: Some(lexer.span()),
                    value: TokenValue::None,
                });
                lexer.begin(Mode::Indented);
            }

            // ── AfterHeader mode ────────────────────────────────────────────
            Rule::HeaderNl => {
                // Newline that closes a header line.
                lexer.yield_token(PrecifiqueToken {
                    token_id: TokenID::Newline,
                    span: Some(lexer.span()),
                    value: TokenValue::None,
                });
                lexer.begin(Mode::Initial);
            }

            // ── Indented mode ────────────────────────────────────────────────
            Rule::QtyAt => {
                // "NNN@" — extract the integer quantity before '@'.
                let text = lexer.take_str()?;
                let qty_str = text.trim_end_matches('@');
                let qty: f64 = qty_str
                    .parse()
                    .map_err(|e| ParlexError::from_err(e, Some(lexer.span())))?;
                lexer.yield_token(PrecifiqueToken {
                    token_id: TokenID::Qtyat,
                    span: Some(lexer.span()),
                    value: TokenValue::Float(qty),
                });
                lexer.begin(Mode::Price);
            }

            Rule::QtyTimes => {
                // "NNNx " — extract the integer quantity before 'x'.
                let text = lexer.take_str()?;
                // Strip trailing 'x' and space: "20x " → "20"
                let qty_str = text.trim_end_matches(|c: char| c == 'x' || c == ' ');
                let qty: f64 = qty_str
                    .parse()
                    .map_err(|e| ParlexError::from_err(e, Some(lexer.span())))?;
                lexer.yield_token(PrecifiqueToken {
                    token_id: TokenID::Qtytimes,
                    span: Some(lexer.span()),
                    value: TokenValue::Float(qty),
                });
                lexer.begin(Mode::CompName);
            }

            // ── Price mode ───────────────────────────────────────────────────
            Rule::Price => {
                // The numeric price, possibly decimal.
                let text = lexer.take_str()?;
                let price: f64 = text
                    .parse()
                    .map_err(|e| ParlexError::from_err(e, Some(lexer.span())))?;
                lexer.yield_token(PrecifiqueToken {
                    token_id: TokenID::Number,
                    span: Some(lexer.span()),
                    value: TokenValue::Float(price),
                });
            }

            Rule::PriceNl => {
                // Newline that closes a material line.
                lexer.yield_token(PrecifiqueToken {
                    token_id: TokenID::Newline,
                    span: Some(lexer.span()),
                    value: TokenValue::None,
                });
                lexer.begin(Mode::Initial);
            }

            // ── CompName mode ────────────────────────────────────────────────
            Rule::CompName => {
                // Rest-of-line component name — trim trailing whitespace.
                let text = lexer.take_str()?;
                let name = text.trim().to_owned();
                lexer.yield_token(PrecifiqueToken {
                    token_id: TokenID::Name,
                    span: Some(lexer.span()),
                    value: TokenValue::Name(name),
                });
            }

            Rule::CompNameNl => {
                // Newline that closes a component line.
                lexer.yield_token(PrecifiqueToken {
                    token_id: TokenID::Newline,
                    span: Some(lexer.span()),
                    value: TokenValue::None,
                });
                lexer.begin(Mode::Initial);
            }

            // ── Special rules ────────────────────────────────────────────────
            Rule::Error => {
                lexer.yield_token(PrecifiqueToken {
                    token_id: TokenID::Error,
                    span: Some(lexer.span()),
                    value: TokenValue::None,
                });
            }

            Rule::End => {
                // EOF — signal the parser to accept.
                lexer.yield_token(PrecifiqueToken {
                    token_id: TokenID::End,
                    span: Some(lexer.span()),
                    value: TokenValue::None,
                });
            }

            Rule::Empty => unreachable!(),
        }
        Ok(())
    }
}

// ─── Wrapper ─────────────────────────────────────────────────────────────────

/// Public lexer wrapper — adapts a byte input stream into a `PrecifiqueToken` stream.
pub struct PrecifiqueLexer<I>
where
    I: TryNextWithContext<(), Item = u8, Error: std::fmt::Display + 'static>,
{
    lexer: Lexer<I, PrecifiqueLexerDriver<I>, ()>,
}

impl<I> PrecifiqueLexer<I>
where
    I: TryNextWithContext<(), Item = u8, Error: std::fmt::Display + 'static>,
{
    pub fn try_new(input: I) -> Result<Self, ParlexError> {
        let driver = PrecifiqueLexerDriver { _marker: PhantomData };
        let lexer = Lexer::try_new(input, driver)?;
        Ok(Self { lexer })
    }
}

impl<I> TryNextWithContext<(), LexerStats> for PrecifiqueLexer<I>
where
    I: TryNextWithContext<(), Item = u8, Error: std::fmt::Display + 'static>,
{
    type Item = PrecifiqueToken;
    type Error = ParlexError;

    fn try_next_with_context(
        &mut self,
        context: &mut (),
    ) -> Result<Option<PrecifiqueToken>, ParlexError> {
        self.lexer.try_next_with_context(context)
    }

    fn stats(&self) -> LexerStats {
        self.lexer.stats()
    }
}
