use anyhow::{Result, anyhow, bail};

use crate::ast::{Component, Entry};

pub fn parse(input: &str) -> Result<Vec<Entry>> {
    let mut entries = Vec::new();
    let mut lines = input.lines().peekable();

    while let Some(line) = lines.next() {
        let name = line.trim().to_string();
        if name.is_empty() {
            continue;
        }

        let mut components: Vec<Component> = Vec::new();
        let mut material: Option<(f64, f64)> = None;

        while let Some(&next_line) = lines.peek() {
            if !next_line.starts_with("    ") {
                break;
            }
            let indented = lines.next().unwrap().trim();

            if let Some(at_pos) = indented.find('@') {
                let qty_str = indented[..at_pos].trim();
                let price_str = indented[at_pos + 1..].trim();
                let qty: f64 = qty_str
                    .parse()
                    .map_err(|_| anyhow!("Invalid quantity: {}", qty_str))?;
                let price: f64 = price_str
                    .parse()
                    .map_err(|_| anyhow!("Invalid price: {}", price_str))?;
                material = Some((qty, price));
            } else if let Some(x_pos) = find_x_separator(indented) {
                let qty_str = indented[..x_pos].trim();
                let cname = indented[x_pos + 1..].trim().to_string();
                let qty: f64 = qty_str
                    .parse()
                    .map_err(|_| anyhow!("Invalid quantity: {}", qty_str))?;
                components.push(Component {
                    quantity: qty,
                    name: cname,
                });
            } else {
                bail!("Invalid indented line: {}", indented);
            }
        }

        if let Some((qty, price)) = material {
            entries.push(Entry::Material {
                name,
                quantity: qty,
                price,
            });
        } else {
            entries.push(Entry::Product { name, components });
        }
    }

    Ok(entries)
}

/// Find the position of `x` that immediately follows digits (e.g. `5x` → 1).
fn find_x_separator(s: &str) -> Option<usize> {
    let bytes = s.as_bytes();
    for (i, &b) in bytes.iter().enumerate() {
        if b == b'x' && i > 0 && bytes[i - 1].is_ascii_digit() {
            return Some(i);
        }
    }
    None
}
