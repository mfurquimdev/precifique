//! Parser for the precifique inventory format.
//!
//! This module wires the ASLR-generated SLR(1) tables (`parser_data`) to a
//! hand-written [`PrecifiqueParserDriver`] that performs semantic reductions.
//!
//! Grammar (see `precifique.g`):
//!
//! ```text
//! doc:   Document  -> EntryList
//! list1: EntryList -> EntryList Entry
//! list2: EntryList -> Entry
//! mat:   Entry     -> name newline indent qtyat number newline
//! prod:  Entry     -> name newline CompLines
//! cl1:   CompLines -> CompLines CompLine
//! cl2:   CompLines -> CompLine
//! comp:  CompLine  -> indent qtytimes name newline
//! ```
//!
//! The parser yields one `PrecifiqueToken` whose `value` is
//! `TokenValue::Entries(Vec<Entry>)` when the entire document has been parsed.

use crate::ast;
use crate::lexer::PrecifiqueLexer;
use crate::token::{PrecifiqueToken, TokenID, TokenValue};
use parlex::{LexerStats, ParlexError, Parser, ParserAction, ParserDriver, ParserStats};
use std::marker::PhantomData;
use try_next::TryNextWithContext;

/// Includes the ASLR-generated SLR(1) tables.
pub mod parser_data {
    include!(concat!(env!("OUT_DIR"), "/parser_data.rs"));
}

use parser_data::{AmbigID, ParData, ProdID, StateID};

// ─── Driver ──────────────────────────────────────────────────────────────────

/// Stateless driver: performs semantic reductions for every grammar production.
pub struct PrecifiqueParserDriver<I> {
    _marker: PhantomData<I>,
}

impl<I> ParserDriver for PrecifiqueParserDriver<I>
where
    I: TryNextWithContext<
            (),
            LexerStats,
            Item = PrecifiqueToken,
            Error: std::fmt::Display + 'static,
        >,
{
    type ParserData = ParData;
    type Token = PrecifiqueToken;
    type Parser = Parser<I, Self, ()>;
    type Context = ();

    fn resolve_ambiguity(
        &mut self,
        _parser: &mut Self::Parser,
        _context: &mut (),
        _ambig: AmbigID,
        _token: &PrecifiqueToken,
    ) -> Result<ParserAction<StateID, ProdID, AmbigID>, ParlexError> {
        unreachable!("precifique grammar has no shift/reduce ambiguities")
    }

    fn reduce(
        &mut self,
        parser: &mut Self::Parser,
        _context: &mut (),
        prod_id: ProdID,
        _token: &PrecifiqueToken,
    ) -> Result<(), ParlexError> {
        match prod_id {
            ProdID::Start => unreachable!(),

            // ── doc: Document -> EntryList ───────────────────────────────────
            ProdID::Doc => {
                let mut list = parser.tokens_pop();
                list.token_id = TokenID::Document;
                parser.tokens_push(list);
            }

            // ── list1: EntryList -> EntryList Entry ──────────────────────────
            ProdID::List1 => {
                let entry_tok = parser.tokens_pop();
                let mut list_tok = parser.tokens_pop();
                let TokenValue::Entry(e) = entry_tok.value else {
                    unreachable!()
                };
                let TokenValue::Entries(ref mut entries) = list_tok.value else {
                    unreachable!()
                };
                entries.push(e);
                parser.tokens_push(list_tok);
            }

            // ── list2: EntryList -> Entry ────────────────────────────────────
            ProdID::List2 => {
                let entry_tok = parser.tokens_pop();
                let TokenValue::Entry(e) = entry_tok.value else {
                    unreachable!()
                };
                parser.tokens_push(PrecifiqueToken {
                    token_id: TokenID::EntryList,
                    span: None,
                    value: TokenValue::Entries(vec![e]),
                });
            }

            // ── mat: Entry -> name newline indent qtyat number newline ────────
            //
            // Stack top-to-bottom when this fires:
            //   [top] newline | number | qtyat | indent | newline | name [bottom]
            ProdID::Mat => {
                let _nl2 = parser.tokens_pop(); // trailing newline
                let number = parser.tokens_pop(); // price
                let qtyat = parser.tokens_pop(); // quantity (@ already stripped)
                let _indent = parser.tokens_pop();
                let _nl1 = parser.tokens_pop(); // first newline
                let name = parser.tokens_pop();

                let TokenValue::Name(n) = name.value else {
                    unreachable!()
                };
                let TokenValue::Float(qty) = qtyat.value else {
                    unreachable!()
                };
                let TokenValue::Float(price) = number.value else {
                    unreachable!()
                };

                let entry = ast::Entry::Material {
                    name: n,
                    quantity: qty,
                    price,
                };
                parser.tokens_push(PrecifiqueToken {
                    token_id: TokenID::Entry,
                    span: None,
                    value: TokenValue::Entry(entry),
                });
            }

            // ── prod: Entry -> name newline CompLines ────────────────────────
            //
            // Stack top-to-bottom: [top] CompLines | newline | name [bottom]
            ProdID::Prod => {
                let comp_lines = parser.tokens_pop();
                let _nl = parser.tokens_pop();
                let name = parser.tokens_pop();

                let TokenValue::Name(n) = name.value else {
                    unreachable!()
                };
                let TokenValue::Components(components) = comp_lines.value else {
                    unreachable!()
                };

                let entry = ast::Entry::Product {
                    name: n,
                    components,
                };
                parser.tokens_push(PrecifiqueToken {
                    token_id: TokenID::Entry,
                    span: None,
                    value: TokenValue::Entry(entry),
                });
            }

            // ── cl1: CompLines -> CompLines CompLine ─────────────────────────
            ProdID::Cl1 => {
                let comp_tok = parser.tokens_pop();
                let mut lines_tok = parser.tokens_pop();
                let TokenValue::Component(c) = comp_tok.value else {
                    unreachable!()
                };
                let TokenValue::Components(ref mut cs) = lines_tok.value else {
                    unreachable!()
                };
                cs.push(c);
                parser.tokens_push(lines_tok);
            }

            // ── cl2: CompLines -> CompLine ───────────────────────────────────
            ProdID::Cl2 => {
                let comp_tok = parser.tokens_pop();
                let TokenValue::Component(c) = comp_tok.value else {
                    unreachable!()
                };
                parser.tokens_push(PrecifiqueToken {
                    token_id: TokenID::CompLines,
                    span: None,
                    value: TokenValue::Components(vec![c]),
                });
            }

            // ── comp: CompLine -> indent qtytimes name newline ────────────────
            //
            // Stack top-to-bottom: [top] newline | name | qtytimes | indent [bottom]
            ProdID::Comp => {
                let _nl = parser.tokens_pop();
                let name = parser.tokens_pop();
                let qtytimes = parser.tokens_pop();
                let _indent = parser.tokens_pop();

                let TokenValue::Name(n) = name.value else {
                    unreachable!()
                };
                let TokenValue::Float(qty) = qtytimes.value else {
                    unreachable!()
                };

                let component = ast::Component {
                    quantity: qty,
                    name: n,
                };
                parser.tokens_push(PrecifiqueToken {
                    token_id: TokenID::CompLine,
                    span: None,
                    value: TokenValue::Component(component),
                });
            }

            // ── vartax: Entry -> name newline vartaxqty ───────────────────────
            //
            // Stack top-to-bottom: [top] VarTaxLines | newline | name [bottom]
            ProdID::VarTax => {
                let var_tax_lines = parser.tokens_pop();
                let _nl = parser.tokens_pop();
                let name = parser.tokens_pop();

                let TokenValue::Name(n) = name.value else {
                    unreachable!()
                };
                let TokenValue::VarTaxs(vartaxs) = var_tax_lines.value else {
                    unreachable!()
                };

                let entry = ast::Entry::Product {
                    name: n,
                    components,
                };
                parser.tokens_push(PrecifiqueToken {
                    token_id: TokenID::Entry,
                    span: None,
                    value: TokenValue::Entry(entry),
                });
            }
        }
        Ok(())
    }
}

// ─── Wrapper ─────────────────────────────────────────────────────────────────

/// Public parser wrapper — drives the full lexer → parser pipeline.
///
/// Call `try_next_with_context(&mut ())` once to get the complete
/// `Document` token (containing all entries), then `None` at EOF.
pub struct PrecifiqueParser<I>
where
    I: TryNextWithContext<(), Item = u8, Error: std::fmt::Display + 'static>,
{
    parser: Parser<PrecifiqueLexer<I>, PrecifiqueParserDriver<PrecifiqueLexer<I>>, ()>,
}

impl<I> PrecifiqueParser<I>
where
    I: TryNextWithContext<(), Item = u8, Error: std::fmt::Display + 'static>,
{
    pub fn try_new(input: I) -> Result<Self, ParlexError> {
        let lexer = PrecifiqueLexer::try_new(input)?;
        let driver = PrecifiqueParserDriver {
            _marker: PhantomData,
        };
        let parser = Parser::new(lexer, driver);
        Ok(Self { parser })
    }
}

impl<I> TryNextWithContext<(), (LexerStats, ParserStats)> for PrecifiqueParser<I>
where
    I: TryNextWithContext<(), Item = u8, Error: std::fmt::Display + 'static>,
{
    type Item = PrecifiqueToken;
    type Error = ParlexError;

    fn try_next_with_context(
        &mut self,
        context: &mut (),
    ) -> Result<Option<PrecifiqueToken>, ParlexError> {
        self.parser.try_next_with_context(context)
    }

    fn stats(&self) -> (LexerStats, ParserStats) {
        self.parser.stats()
    }
}
