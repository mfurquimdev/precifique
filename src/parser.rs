use parlex::parser;

parser! {
    pub grammar PrecifiqueParser for Token {
        pub entries: Vec<Entry> = {
            let mut v = Vec::new();
            while let Some(e) = entry() {
                v.push(e);
            }
            v
        };

        entry: Entry = {
            let name = expect_name();
            expect_newline();

            let mut components = Vec::new();
            let mut material = None;

            while peek_indent() {
                expect_indent();

                if peek_number() && peek_at() {
                    let qty = expect_number();
                    expect_at();
                    let price = expect_number();
                    material = Some((qty, price));
                } else {
                    let qty = expect_number();
                    expect_x();
                    let cname = expect_name();
                    components.push(Component {
                        quantity: qty,
                        name: cname,
                    });
                }

                expect_newline();
            }

            if let Some((q, p)) = material {
                Entry::Material {
                    name,
                    quantity: q,
                    price: p,
                }
            } else {
                Entry::Product {
                    name,
                    components,
                }
            }
        };
    }
}
