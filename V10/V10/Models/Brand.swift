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
        
        guard let url = URL(string: "http://localhost:8005/brands") else {
            print("Invalid URL")
            return
        }
        
        URLSession.shared.dataTask(with: url) { [weak self] data, response, error in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                if let error = error {
                    self?.error = error
                    return
                }
                
                guard let data = data else {
                    print("No data received")
                    return
                }
                
                do {
                    let brands = try JSONDecoder().decode([Brand].self, from: data)
                    self?.brands = brands
                } catch {
                    print("Decoding error: \(error)")
                    self?.error = error
                }
            }
        }.resume()
    }
} 