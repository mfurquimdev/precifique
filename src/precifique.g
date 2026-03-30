-- Grammar for the precifique inventory format (ASLR / SLR(1)).
--
-- The top-level nonterminal is Document.  The parser yields one Document
-- token (containing all parsed entries) when it sees the End marker at EOF.
--
-- Terminals (lowercase):   name  newline  indent  qtyat  number  qtytimes
-- Nonterminals (Title):    Document  EntryList  Entry  CompLines  CompLine

-- Document wraps the complete list of entries.
doc:   Document  -> EntryList

-- EntryList accumulates entries left-recursively.
list1: EntryList -> EntryList Entry
list2: EntryList -> Entry

-- A material entry: one indented line with quantity@price.
mat:  Entry -> name newline indent qtyat number newline

-- A product entry: one or more component lines.
prod: Entry -> name newline CompLines

-- CompLines accumulates component lines left-recursively.
cl1: CompLines -> CompLines CompLine
cl2: CompLines -> CompLine

-- A single component line: NNNx ComponentName.
comp: CompLine -> indent qtytimes name newline
