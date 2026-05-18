use anyhow::{Result, anyhow};
use std::collections::HashMap;

use crate::ast::{Component, Entry};

pub struct PrecifiqueEngine {
    materials: HashMap<String, (f64, f64)>,
    products: HashMap<String, Vec<Component>>,
    taxes: HashMap<String, f64>,
}

impl PrecifiqueEngine {
    pub fn new(entries: Vec<Entry>) -> Self {
        let mut materials = HashMap::new();
        let mut products = HashMap::new();
        let mut taxes = HashMap::new();

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
                Entry::Tax { name, percent } => {
                    taxes.insert(name, percent);
                }
            }
        }

        Self {
            materials,
            products,
            taxes,
        }
    }

    pub fn unit_cost(&self, name: &str) -> Result<f64> {
        if let Some((qty, price)) = self.materials.get(name) {
            return Ok(price / qty);
        }

        if let Some(components) = self.products.get(name) {
            let mut sub_total = 0.0;

            for c in components {
                let unit = self.unit_cost(&c.name)?;
                sub_total += unit * c.quantity;
            }

            let mut taxes = 0.0;

            for (_tax_name, tax_value) in &self.taxes {
                taxes += tax_value / 100.0;
            }

            // let total = sub_total / (1.0 - taxes);
            let total = sub_total * (1.0 + taxes);

            return Ok(total);
        }

        if let Some(tax) = self.taxes.get(name) {
            return Ok(*tax);
        }

        Err(anyhow!("Unknown item: {}", name))
    }
}
