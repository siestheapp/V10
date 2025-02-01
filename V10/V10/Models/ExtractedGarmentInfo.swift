import Foundation

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
    
    var description: String {
        """
        Product Code: \(productCode ?? "none")
        Name: \(name ?? "none")
        Size: \(size ?? "none")
        Color: \(color ?? "none")
        Price: \(price.map(String.init) ?? "none")
        Materials: \(materials)
        Measurements: \(measurements)
        """
    }
} 