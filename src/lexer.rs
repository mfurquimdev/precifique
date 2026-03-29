use parlex::lexer;

/// Entry        := Name '\n' IndentedLine+
/// IndentedLine := INDENT MaterialDef | INDENT ProductUse
///
/// MaterialDef  := Quantity '@' Price
/// ProductUse   := Quantity 'x' Name
///
/// Semantics
/// Material: has (quantity, total_price) → unit cost = price / quantity
/// Product: list of (quantity_used, reference_name)
/// Resolution is recursive (products can reference materials or other products)
lexer! {
    pub enum Token {
        Indent => r"[ ]{4}",
        Newline => r"\n",
        At => r"@",
        X => r"x",
        Number => r"[0-9]+(\.[0-9]+)?",
        Name => r"[A-Za-zÀ-ÿ0-9 ]+",
        Blank => r"\n\s*\n",
        Whitespace => r"[ \t]+",
    }

    ignore Whitespace;
}
