use anyhow::{Result, anyhow};
use std::collections::HashMap;

use crate::ast::{Component, Entry};

pub struct PrecifiqueEngine {
    materials: HashMap<String, (f64, f64)>,
    products: HashMap<String, Vec<Component>>,
}

impl PrecifiqueEngine {
    pub fn new(entries: Vec<Entry>) -> Self {
        let mut materials = HashMap::new();
        let mut products = HashMap::new();

        for e in entries {
            match e {
                Entry::Material {
                    name,
                    quantity,
                    price,
                } => {
                    materials.insert(name, (quantity, price));
                }
                Entry::Product { name, components } => {
                    products.insert(name, components);
                }
            }
        }

        Self {
            materials,
            products,
        }
    }

    pub fn unit_cost(&self, name: &str) -> Result<f64> {
        if let Some((qty, price)) = self.materials.get(name) {
            return Ok(price / qty);
        }

        if let Some(components) = self.products.get(name) {
            let mut total = 0.0;

            for c in components {
                let unit = self.unit_cost(&c.name)?;
                total += unit * c.quantity;
            }

            return Ok(total);
        }

        Err(anyhow!("Unknown item: {}", name))
    }
}
