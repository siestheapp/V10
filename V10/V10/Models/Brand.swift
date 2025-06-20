import Foundation

struct Brand: Identifiable, Codable {
    let id: Int
    let name: String
    let categories: [String]
    let measurements: [String]
    
    enum CodingKeys: String, CodingKey {
        case id
        case name
        case categories
        case measurements
    }
}

class BrandStore: ObservableObject {
    @Published var brands: [Brand] = []
    @Published var isLoading = false
    @Published var error: Error?
    
    func fetchBrands() {
        isLoading = true
        error = nil
        
        guard let url = URL(string: "\(Config.baseURL)/brands") else {
            print("Invalid URL")
            self.error = NSError(domain: "AppError", code: 1, userInfo: [NSLocalizedDescriptionKey: "Invalid base URL"])
            self.isLoading = false
            return
        }
        
        let task = URLSession.shared.dataTask(with: url) { [weak self] data, response, error in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                if let error = error {
                    print("Network error: \(error)")
                    self?.error = error
                    return
                }
                
                guard let data = data else {
                    print("No data received")
                    return
                }
                
                // Debug: Print raw response
                if let rawString = String(data: data, encoding: .utf8) {
                    print("Raw response data: \(rawString)")
                }
                
                // Check if response is an error message
                if let errorDict = try? JSONDecoder().decode([String: String].self, from: data),
                   let detail = errorDict["detail"] {
                    print("Server error: \(detail)")
                    self?.error = NSError(domain: "ServerError", code: -1, userInfo: [NSLocalizedDescriptionKey: detail])
                    return
                }
                
                do {
                    let decoder = JSONDecoder()
                    let brands = try decoder.decode([Brand].self, from: data)
                    print("Successfully decoded \(brands.count) brands")
                    self?.brands = brands
                } catch {
                    print("Decoding error: \(error)")
                    self?.error = error
                }
            }
        }
        
        task.resume()
    }
} 