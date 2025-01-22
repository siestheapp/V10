import Foundation

// Model for extracted raw data from OCR
struct ExtractedGarmentInfo: Codable, CustomStringConvertible {
    var productCode: String?
    var name: String?
    var size: String?
    var color: String?
    var materials: [String: Int]
    var price: Double?
    var measurements: [String: String]
    var rawText: String
    
    init() {
        self.materials = [:]
        self.measurements = [:]
        self.rawText = ""
    }
    
    // Implement CustomStringConvertible
    var description: String {
        let productCodeStr: String = "Product Code: " + (productCode ?? "none")
        let nameStr: String = "Name: " + (name ?? "none")
        let sizeStr: String = "Size: " + (size ?? "none")
        let colorStr: String = "Color: " + (color ?? "none")
        let priceStr: String = "Price: " + (price.map { String(format: "%.2f", $0) } ?? "none")
        let materialsStr: String = "Materials: " + materials.description
        let measurementsStr: String = "Measurements: " + measurements.description
        
        let lines: [String] = [
            productCodeStr,
            nameStr,
            sizeStr,
            colorStr,
            priceStr,
            materialsStr,
            measurementsStr
        ]
        
        return lines.joined(separator: "\n")
    }
}

// Model for processed garment data
struct UniqloGarment: Codable {
    let id: String
    let name: String
    let brand: String
    let size: String
    let category: String
    let subcategory: String
    let color: String
    let price: Double
    let imageUrl: String
    let productUrl: String
    
    init(
        id: String,
        name: String,
        brand: String = "UNIQLO",
        size: String,
        category: String = "",
        subcategory: String = "",
        color: String,
        price: Double,
        imageUrl: String = "",
        productUrl: String = ""
    ) {
        self.id = id
        self.name = name
        self.brand = brand
        self.size = size
        self.category = category
        self.subcategory = subcategory
        self.color = color
        self.price = price
        self.imageUrl = imageUrl
        self.productUrl = productUrl
    }
} 