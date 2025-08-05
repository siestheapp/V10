// ScanTab.swift
// Handles garment scanning & manual product entry.
// - If the user scans a tag, stays on ScanTab & opens ScanGarmentView.swift.
// - If the user pastes a product link, gets smart size recommendation.

import SwiftUI

struct ScanTab: View {
    @State private var showingOptions = false
    @State private var showingImagePicker = false
    @State private var showingScanView = false
    @State private var showingBrandsView = false
    @State private var selectedImage: UIImage?
    @State private var productLink: String = ""
    @State private var sizeRecommendation: SizeRecommendationResponse?
    @State private var isAnalyzing = false
    @State private var analysisError: String?
    @State private var navigateToFitFeedback = false

    var body: some View {
        NavigationView {
            VStack(spacing: 30) {
                // Scan Tag Section
                VStack(spacing: 15) {
                    Text("Scan")
                        .font(.largeTitle)
                        .bold()
                    
                    Button(action: {
                        showingOptions = true
                    }) {
                        Text("Scan a Tag")
                            .font(.headline)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.blue)
                            .cornerRadius(10)
                    }
                    .padding(.horizontal, 40)
                    .sheet(isPresented: $showingImagePicker) {
                        ImagePicker(image: $selectedImage)
                    }
                    .onChange(of: selectedImage) { newImage in
                        if newImage != nil {
                            showingScanView = true
                        }
                    }
                    .sheet(isPresented: $showingScanView) {
                        if let image = selectedImage {
                            NavigationView {
                                ScanGarmentView(
                                    selectedImage: image,
                                    isPresented: $showingScanView
                                )
                            }
                        }
                    }
                }
                
                // Divider
                HStack {
                    Rectangle()
                        .frame(height: 1)
                        .foregroundColor(.gray)
                    Text("OR")
                        .foregroundColor(.gray)
                        .padding(.horizontal)
                    Rectangle()
                        .frame(height: 1)
                        .foregroundColor(.gray)
                }
                .padding(.horizontal, 40)
                
                // Smart Size Recommendation Section
                VStack(alignment: .leading, spacing: 15) {
                    Text("Get Size Recommendation")
                        .font(.headline)
                        .frame(maxWidth: .infinity, alignment: .leading)
                    
                    // URL Input
                    HStack {
                        TextField("Paste product link here", text: $productLink)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .disabled(isAnalyzing)
                        
                        if !productLink.isEmpty && !isAnalyzing {
                            Button("Analyze") {
                                analyzeProduct()
                            }
                            .buttonStyle(.borderedProminent)
                        }
                    }
                    .padding(.horizontal, 20)
                    
                    // Analysis Status
                    if isAnalyzing {
                        HStack {
                            ProgressView()
                                .scaleEffect(0.8)
                            Text("Analyzing product and finding your best size...")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        .padding(.horizontal, 20)
                    }
                    
                    // Error Display
                    if let error = analysisError {
                        Text(error)
                            .font(.caption)
                            .foregroundColor(.red)
                            .padding(.horizontal, 20)
                    }
                    
                    // Size Recommendation Display
                    if let recommendation = sizeRecommendation {
                        SizeRecommendationView(recommendation: recommendation)
                    }
                }
                .padding(.horizontal, 40)
                
                Spacer()
                
                // Proceed Button (only shown when we have a recommendation)
                if let recommendation = sizeRecommendation {
                    Button(action: {
                        navigateToFitFeedback = true
                    }) {
                        Text("Add to Closet - Size \(recommendation.recommendedSize)")
                            .font(.headline)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.green)
                            .cornerRadius(10)
                    }
                    .padding(.horizontal, 40)
                    .background(
                        NavigationLink(
                            destination: FitFeedbackView(
                                feedbackType: .manualEntry, 
                                selectedSize: recommendation.recommendedSize,
                                productUrl: recommendation.productUrl,
                                brand: recommendation.brand
                            ),
                            isActive: $navigateToFitFeedback
                        ) { EmptyView() }
                    )
                }
            }
            .padding(.top, 30)
            .navigationTitle("Scan")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        showingBrandsView = true
                    }) {
                        HStack {
                            Image(systemName: "tag")
                            Text("Brands")
                        }
                    }
                }
            }
            .sheet(isPresented: $showingBrandsView) {
                NavigationView {
                    BrandsView()
                }
            }
            .confirmationDialog("Choose an option", isPresented: $showingOptions) {
                Button("Open Camera") {
                    showingImagePicker = true
                }
                
                Button("Choose from Photos") {
                    showingImagePicker = true
                }
            }
        }
    }
    
    private func analyzeProduct() {
        guard !productLink.isEmpty else { return }
        
        isAnalyzing = true
        analysisError = nil
        sizeRecommendation = nil
        
        guard let url = URL(string: "\(Config.baseURL)/garment/size-recommendation") else {
            analysisError = "Invalid API URL"
            isAnalyzing = false
            return
        }
        
        let requestBody = [
            "product_url": productLink,
            "user_id": "1"  // Using default user for now
        ]
        
        guard let jsonData = try? JSONSerialization.data(withJSONObject: requestBody) else {
            analysisError = "Failed to encode request"
            isAnalyzing = false
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = jsonData
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                isAnalyzing = false
                
                if let error = error {
                    analysisError = "Network error: \(error.localizedDescription)"
                    return
                }
                
                guard let data = data else {
                    analysisError = "No data received"
                    return
                }
                
                do {
                    let recommendation = try JSONDecoder().decode(SizeRecommendationResponse.self, from: data)
                    self.sizeRecommendation = recommendation
                } catch {
                    analysisError = "Failed to parse recommendation: \(error.localizedDescription)"
                    print("Decode error: \(error)")
                }
            }
        }.resume()
    }
}

// Size Recommendation Display Component
struct SizeRecommendationView: View {
    let recommendation: SizeRecommendationResponse
    
    // Get top 2 sizes for display
    private var topTwoSizes: [DirectSizeOption] {
        let sorted = recommendation.allSizes.sorted { $0.overallFitScore > $1.overallFitScore }
        return Array(sorted.prefix(2))
    }
    
    // Get recommended size details for enhanced display
    private var recommendedSizeDetails: DirectSizeOption? {
        recommendation.allSizes.first { $0.size == recommendation.recommendedSize }
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Header
            HStack {
                Text("📏 Size Recommendation")
                    .font(.headline)
                    .foregroundColor(.primary)
                Spacer()
                Text(recommendation.brand)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
            
            // Enhanced Main Recommendation
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    VStack(alignment: .leading) {
                        Text("Recommended Size")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Text(recommendation.recommendedSize)
                            .font(.system(size: 32, weight: .bold))
                            .foregroundColor(.green)
                    }
                    
                    Spacer()
                    
                    VStack(alignment: .trailing) {
                        Text("Fit Score")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Text(String(format: "%.1f%%", recommendation.recommendedFitScore * 100))
                            .font(.title2)
                            .fontWeight(.bold)
                            .foregroundColor(scoreColor(for: recommendation.recommendedFitScore))
                    }
                }
                
                // Show size guide measurements vs user ranges for recommended size
                if let recommended = recommendedSizeDetails {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Size Guide vs Your Ranges:")
                            .font(.caption)
                            .fontWeight(.medium)
                            .foregroundColor(.secondary)
                        
                        // Parse measurement summary to show comparison
                        let measurements = parseMeasurementSummary(recommended.measurementSummary)
                        ForEach(measurements, id: \.dimension) { measurement in
                            HStack {
                                Text(measurement.dimension.capitalized)
                                    .font(.caption)
                                    .fontWeight(.medium)
                                Spacer()
                                Text("\(measurement.value)\"")
                                    .font(.caption)
                                    .foregroundColor(.primary)
                                Text("vs")
                                    .font(.caption2)
                                    .foregroundColor(.secondary)
                                Text("\(measurement.userRange)")
                                    .font(.caption)
                                    .foregroundColor(.blue)
                            }
                        }
                    }
                    .padding(.top, 4)
                }
            }
            .padding()
            .background(Color(.systemGray6))
            .cornerRadius(12)
            
            // Primary Concerns (if any)
            if !recommendation.primaryConcerns.isEmpty {
                HStack {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .foregroundColor(.orange)
                    Text("Potential concerns: \(recommendation.primaryConcerns.joined(separator: ", "))")
                        .font(.caption)
                        .foregroundColor(.orange)
                }
                .padding(.horizontal)
            }
            
            // Reasoning
            Text(recommendation.reasoning)
                .font(.caption)
                .foregroundColor(.secondary)
            
            // Fixed Reference Garments - Only show for recommended size
            if let recommended = recommendedSizeDetails {
                DisclosureGroup("Reference Garments (\(recommendation.referenceGarments.count) used)") {
                    VStack(alignment: .leading, spacing: 6) {
                        ForEach(Array(recommendation.referenceGarments.keys.sorted()), id: \.self) { key in
                            if let reference = recommendation.referenceGarments[key] {
                                VStack(alignment: .leading, spacing: 2) {
                                    HStack {
                                        Circle().fill(.blue).frame(width: 8, height: 8)
                                        Text("\(reference.brand) \(reference.size)")
                                            .fontWeight(.medium)
                                        Spacer()
                                        Text("\(String(format: "%.0f%%", reference.confidence * 100)) confidence")
                                            .font(.caption2)
                                            .foregroundColor(.secondary)
                                    }
                                    
                                    // Show measurements for recommended size only
                                    if !reference.measurements.isEmpty {
                                        let measurementText = reference.measurements.map { dim, measurement in
                                            "\(dim): \(measurement)"
                                        }.joined(separator: ", ")
                                        
                                        Text(measurementText)
                                            .font(.caption2)
                                            .foregroundColor(.secondary)
                                            .padding(.leading, 16)
                                    }
                                }
                            }
                        }
                    }
                    .font(.caption)
                }
                .font(.caption)
            }
            
            // Limited Alternative Sizes - Only top 2
            if topTwoSizes.count > 1 {
                DisclosureGroup("Alternative Sizes (Top 2 Matches)") {
                    LazyVGrid(columns: [
                        GridItem(.flexible()),
                        GridItem(.flexible())
                    ], spacing: 8) {
                        ForEach(topTwoSizes, id: \.size) { size in
                            VStack(alignment: .leading, spacing: 4) {
                                HStack {
                                    Text(size.size)
                                        .font(.headline)
                                        .fontWeight(size.size == recommendation.recommendedSize ? .bold : .regular)
                                    Spacer()
                                    Text(String(format: "%.0f%%", size.overallFitScore * 100))
                                        .font(.caption)
                                        .foregroundColor(scoreColor(for: size.overallFitScore))
                                }
                                
                                Text(size.fitType.capitalized)
                                    .font(.caption)
                                    .foregroundColor(fitColor(for: size.fitType))
                                
                                Text(size.measurementSummary)
                                    .font(.caption2)
                                    .foregroundColor(.secondary)
                                    .lineLimit(2)
                                
                                if !size.primaryConcerns.isEmpty {
                                    HStack {
                                        Image(systemName: "exclamationmark.triangle.fill")
                                            .font(.caption2)
                                            .foregroundColor(.orange)
                                        Text(size.primaryConcerns.joined(separator: ", "))
                                            .font(.caption2)
                                            .foregroundColor(.orange)
                                            .lineLimit(1)
                                    }
                                }
                            }
                            .padding(8)
                            .background(
                                Color(size.size == recommendation.recommendedSize ? .systemGray4 : .systemGray6)
                            )
                            .cornerRadius(8)
                        }
                    }
                }
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(16)
        .shadow(color: .black.opacity(0.1), radius: 4, x: 0, y: 2)
    }
    
    // Helper to parse measurement summary for comparison display
    private func parseMeasurementSummary(_ summary: String) -> [MeasurementComparison] {
        let components = summary.components(separatedBy: ", ")
        return components.compactMap { component in
            let parts = component.components(separatedBy: ": ")
            guard parts.count == 2 else { return nil }
            
            let dimension = parts[0].trimmingCharacters(in: .whitespaces)
            let value = parts[1].trimmingCharacters(in: .whitespaces)
            
            // Get user range for this dimension from fit zones
            let userRange = getUserFitZoneRange(for: dimension)
            
            return MeasurementComparison(
                dimension: dimension,
                value: value,
                userRange: userRange
            )
        }
    }
    
    // Helper to get user fit zone range for a dimension
    private func getUserFitZoneRange(for dimension: String) -> String {
        // Use the established fit zones from the documentation
        switch dimension.lowercased() {
        case "chest":
            return "39.5-42.0\""  // From fitzonetracker.md
        case "neck":
            return "16.0-16.5\""  // From fitzonetracker.md
        case "sleeve":
            return "33.5-36.0\""  // From fitzonetracker.md
        default:
            return "N/A"
        }
    }
    
    private func fitColor(for fitType: String) -> Color {
        switch fitType.lowercased() {
        case "tight": return .orange
        case "good": return .green  
        case "relaxed": return .blue
        case "too_loose": return .red
        case "excellent": return .green
        case "acceptable": return .orange
        case "poor": return .red
        default: return .gray
        }
    }
    
    private func scoreColor(for score: Double) -> Color {
        if score >= 0.8 {
            return .green
        } else if score >= 0.6 {
            return .orange
        } else {
            return .red
        }
    }
}

// Helper struct for measurement comparison
struct MeasurementComparison {
    let dimension: String
    let value: String
    let userRange: String
}

// Data Models for Size Recommendation (Direct Garment Comparison)
struct SizeRecommendationResponse: Codable {
    let productUrl: String
    let brand: String
    let analysisType: String
    let dimensionsAnalyzed: [String]
    let referenceGarments: [String: ReferenceGarment]
    let recommendedSize: String
    let recommendedFitScore: Double
    let confidence: Double
    let reasoning: String
    let primaryConcerns: [String]
    let comprehensiveAnalysis: Bool
    let allSizes: [DirectSizeOption]
    
    enum CodingKeys: String, CodingKey {
        case productUrl = "product_url"
        case brand
        case analysisType = "analysis_type"
        case dimensionsAnalyzed = "dimensions_analyzed"
        case referenceGarments = "reference_garments"
        case recommendedSize = "recommended_size"
        case recommendedFitScore = "recommended_fit_score"
        case confidence
        case reasoning
        case primaryConcerns = "primary_concerns"
        case comprehensiveAnalysis = "comprehensive_analysis"
        case allSizes = "all_sizes"
    }
}

struct ReferenceGarment: Codable {
    let brand: String
    let size: String
    let productName: String
    let measurements: [String: String]  // Now stores range strings like "16-16.5\""
    let feedback: [String: String]
    let confidence: Double
    
    enum CodingKeys: String, CodingKey {
        case brand
        case size
        case productName = "product_name"
        case measurements
        case feedback
        case confidence
    }
}

struct DirectSizeOption: Codable {
    let size: String
    let overallFitScore: Double
    let confidence: Double
    let fitType: String
    let availableDimensions: [String]
    let dimensionAnalysis: [String: DimensionComparison]
    let measurementSummary: String
    let reasoning: String
    let primaryConcerns: [String]
    let fitDescription: String
    
    enum CodingKeys: String, CodingKey {
        case size
        case overallFitScore = "overall_fit_score"
        case confidence
        case fitType = "fit_type"
        case availableDimensions = "available_dimensions"
        case dimensionAnalysis = "dimension_analysis"
        case measurementSummary = "measurement_summary"
        case reasoning
        case primaryConcerns = "primary_concerns"
        case fitDescription = "fit_description"
    }
}

struct DimensionComparison: Codable {
    let type: String
    let fitScore: Double
    let garmentMeasurement: Double
    let explanation: String
    let fitZone: String?
    let zoneRange: String?  // API returns "39.5-42.5" string format
    let matchesPreference: Bool?
    
    enum CodingKeys: String, CodingKey {
        case type
        case fitScore = "fit_score"
        case garmentMeasurement = "garment_measurement"
        case explanation
        case fitZone = "fit_zone"
        case zoneRange = "zone_range"
        case matchesPreference = "matches_preference"
    }
}

// RangeComparisonDetails removed - no longer needed with new DimensionComparison structure

#Preview {
    ScanTab()
}
