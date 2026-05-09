#[derive(Debug, Clone)]
pub enum Entry {
    Material {
        name: String,
        quantity: f64,
        price: f64,
    },
    Product {
        name: String,
        components: Vec<Component>,
    },
    Tax {
        name: String,
        percent: f64,
    },
}

#[derive(Debug, Clone)]
pub struct Component {
    pub quantity: f64,
    pub name: String,
}
