use crate::ast;
use parlex::{Span, Token};

// TokenID is generated from precifique.g by the ASLR parser generator.
// Re-exported here so lexer.rs can use it without going through parser::parser_data.
pub use crate::parser::parser_data::TokenID;

/// Semantic values carried by tokens through lexing and parsing.
#[derive(Debug, Clone)]
pub enum TokenValue {
    /// No payload (Newline, Indent, and non-terminal placeholders).
    None,
    /// A name string (header lines and component name lines).
    Name(String),
    /// A floating-point number (quantities and prices).
    Float(f64),
    /// A single parsed component (CompLine non-terminal).
    Component(ast::Component),
    /// A list of components (CompLines non-terminal).
    Components(Vec<ast::Component>),
    /// A single parsed tax (axLine non-terminal).
    Tax(ast::Tax),
    /// A list of taxes (TaxLines non-terminal).
    Taxs(Vec<ast::Tax>),
    /// A single parsed entry (Entry non-terminal).
    Entry(ast::Entry),
    /// The full list of entries (EntryList / Document non-terminal).
    Entries(Vec<ast::Entry>),
}

/// The single token type shared by the lexer and parser.
#[derive(Debug, Clone)]
pub struct PrecifiqueToken {
    pub token_id: TokenID,
    pub value: TokenValue,
    pub span: Option<Span>,
}

impl Token for PrecifiqueToken {
    type TokenID = TokenID;

    fn token_id(&self) -> TokenID {
        self.token_id
    }

    fn span(&self) -> Option<Span> {
        self.span
    }
}
