// ScanTab.swift
// Handles garment scanning & manual product entry.
// - If the user scans a tag, stays on ScanTab & opens ScanGarmentView.swift.
// - If the user pastes a product link, gets smart size recommendation.

import SwiftUI

// MARK: - Data Models (moved to top for proper scope)

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
    
    // 🎯 NEW: Enhanced confidence and explanation system
    let confidenceTier: ConfidenceTier?
    let humanExplanation: String?
    let alternativeExplanations: [AlternativeExplanation]?
    
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
        case confidenceTier = "confidence_tier"
        case humanExplanation = "human_explanation"
        case alternativeExplanations = "alternative_explanations"
    }
}

// 🎯 NEW: Confidence tier model for better UX
struct ConfidenceTier: Codable {
    let tier: String
    let confidenceScore: Double
    let label: String
    let icon: String
    let color: String
    let description: String
    
    enum CodingKeys: String, CodingKey {
        case tier
        case confidenceScore = "confidence_score"
        case label
        case icon
        case color
        case description
    }
}

// 🎯 NEW: Alternative size explanations
struct AlternativeExplanation: Codable {
    let size: String
    let explanation: String
    let fitScore: Double
    
    enum CodingKeys: String, CodingKey {
        case size
        case explanation
        case fitScore = "fit_score"
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

// MARK: - Views

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
                    let confidenceInfo = recommendation.confidenceTier ?? ConfidenceTier(
                        tier: "fair", confidenceScore: recommendation.confidence,
                        label: "Good Fit", icon: "✅", color: "green", description: "This should work for you"
                    )
                    
                    Button(action: {
                        navigateToFitFeedback = true
                    }) {
                        Text("\(confidenceInfo.icon) Add Size \(recommendation.recommendedSize) to Closet")
                            .font(.headline)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(colorFromString(confidenceInfo.color))
                            .cornerRadius(12)
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
    
    // Helper function to convert string color to SwiftUI Color (for button)
    private func colorFromString(_ colorString: String) -> Color {
        switch colorString.lowercased() {
        case "green":
            return .green
        case "orange":
            return .orange
        case "red":
            return .red
        case "blue":
            return .blue
        default:
            return .green
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

// MARK: - Size Recommendation Display Component (todoAug.md implementation)
struct SizeRecommendationView: View {
    let recommendation: SizeRecommendationResponse
    @State private var showDetailedAnalysis = false
    @State private var showAlternativeSizes = false
    
    // Get confidence tier info with fallback
    private var confidenceInfo: ConfidenceTier {
        recommendation.confidenceTier ?? ConfidenceTier(
            tier: "fair",
            confidenceScore: recommendation.confidence,
            label: "Good Fit",
            icon: "✅",
            color: "green",
            description: "This should work for you"
        )
    }
    
    // Get enhanced explanation showing analyzed dimensions and actual reference garments
    private var explanation: String {
        // Get analyzed dimensions from the recommendation
        let analyzedDimensions = getAnalyzedDimensions()
        let referenceGarment = getBestReferenceGarment()
        
        if !analyzedDimensions.isEmpty && !referenceGarment.isEmpty {
            let dimensionText = analyzedDimensions.count > 1 ? 
                "Analyzed \(analyzedDimensions.joined(separator: ", "))" : 
                "Based on \(analyzedDimensions.first!)"
            return "\(dimensionText) - \(referenceGarment)"
        }
        
        // Fallback to original explanation
        return recommendation.humanExplanation ?? recommendation.reasoning
    }
    
    // Helper to get analyzed dimensions from the recommendation
    private func getAnalyzedDimensions() -> [String] {
        var dimensions: [String] = []
        
        // Check if we have dimension analysis data
        if let recommended = recommendation.allSizes.first(where: { $0.size == recommendation.recommendedSize }) {
            // Parse available dimensions from the recommendation
            if recommended.measurementSummary.contains("chest") || recommended.measurementSummary.contains("Chest") {
                dimensions.append("chest")
            }
            if recommended.measurementSummary.contains("neck") || recommended.measurementSummary.contains("Neck") {
                dimensions.append("neck")  
            }
            if recommended.measurementSummary.contains("sleeve") || recommended.measurementSummary.contains("Sleeve") {
                dimensions.append("sleeve")
            }
        }
        
        return dimensions
    }
    
    // Helper to get the best reference garment description
    private func getBestReferenceGarment() -> String {
        guard !recommendation.referenceGarments.isEmpty else {
            return "matches your measurements"
        }
        
        // Find same-brand reference first (highest confidence)
        let sameBrandRef = recommendation.referenceGarments.values.first { ref in
            ref.brand.lowercased() == recommendation.brand.lowercased()
        }
        
        if let sameBrandRef = sameBrandRef {
            return "matches your \(sameBrandRef.brand) \(sameBrandRef.size)"
        }
        
        // Otherwise use highest confidence reference
        let bestRef = recommendation.referenceGarments.values.max { $0.confidence < $1.confidence }
        if let bestRef = bestRef {
            return "similar to your \(bestRef.brand) \(bestRef.size)"
        }
        
        return "based on your closet"
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            // Header with just brand (no "Size Recommendation" title)
            HStack {
                Spacer()
                Text(recommendation.brand)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
            
            // 🎯 PRIMARY DISPLAY: Lead with confidence + size (per todoAug.md)
            VStack(alignment: .leading, spacing: 12) {
                // Main recommendation - confidence and size together
                HStack(alignment: .center, spacing: 8) {
                    Text(confidenceInfo.icon)
                        .font(.title)
                    
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Size \(recommendation.recommendedSize)")
                            .font(.system(size: 32, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text(confidenceInfo.label)
                            .font(.headline)
                            .foregroundColor(colorFromString(confidenceInfo.color))
                    }
                    
                    Spacer()
                }
                
                // Human-readable explanation (anxiety-reducing language per todoAug.md)
                Text(explanation)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .lineLimit(2)
                    .multilineTextAlignment(.leading)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color(.systemGray6))
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(colorFromString(confidenceInfo.color).opacity(0.3), lineWidth: 2)
                    )
            )
            
            // 🎯 PROGRESSIVE DISCLOSURE: Expandable sections (per todoAug.md)
            VStack(spacing: 8) {
                // Why this size?
                DisclosureGroup("Why this size?", isExpanded: $showDetailedAnalysis) {
                    VStack(alignment: .leading, spacing: 8) {
                        // Show analyzed dimensions with clear indicators
                        let analyzedDimensions = getAnalyzedDimensions()
                        if !analyzedDimensions.isEmpty {
                            Text("Measurements analyzed:")
                                .font(.caption)
                                .fontWeight(.medium)
                                .foregroundColor(.secondary)
                            
                            ForEach(analyzedDimensions, id: \.self) { dimension in
                                HStack {
                                    Text("✅")
                                        .font(.caption)
                                    Text(dimension.capitalized)
                                        .font(.caption)
                                        .fontWeight(.medium)
                                    Text("matches your fit zone")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                    Spacer()
                                }
                            }
                        } else if let recommended = recommendation.allSizes.first(where: { $0.size == recommendation.recommendedSize }) {
                            // Fallback to original measurement display
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
                        
                        // Reference garments (contextual explanations per todoAug.md)
                        if !recommendation.referenceGarments.isEmpty {
                            Text("Based on:")
                                .font(.caption)
                                .fontWeight(.medium)
                                .padding(.top, 4)
                            
                            ForEach(Array(recommendation.referenceGarments.keys.sorted()), id: \.self) { key in
                                if let reference = recommendation.referenceGarments[key] {
                                    HStack {
                                        Circle().fill(.blue).frame(width: 6, height: 6)
                                        Text("\(reference.brand) \(reference.size)")
                                            .font(.caption)
                                        Spacer()
                                        Text("\(String(format: "%.0f%%", reference.confidence * 100)) match")
                                            .font(.caption2)
                                            .foregroundColor(.secondary)
                                    }
                                }
                            }
                        }
                    }
                    .padding(.top, 8)
                }
                .font(.subheadline)
                .foregroundColor(.primary)
                
                // Alternative sizes (per todoAug.md)
                if let alternatives = recommendation.alternativeExplanations, !alternatives.isEmpty {
                    DisclosureGroup("Other sizes?", isExpanded: $showAlternativeSizes) {
                        VStack(alignment: .leading, spacing: 6) {
                            ForEach(alternatives, id: \.size) { alt in
                                HStack(alignment: .top) {
                                    Text(alt.size)
                                        .font(.subheadline)
                                        .fontWeight(.medium)
                                    Spacer()
                                    Text(alt.explanation)
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                        .multilineTextAlignment(.trailing)
                                }
                                .padding(.vertical, 2)
                            }
                        }
                        .padding(.top, 8)
                    }
                    .font(.subheadline)
                    .foregroundColor(.primary)
                }
            }
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 8)
                .fill(Color(.systemBackground))
                .shadow(color: .black.opacity(0.1), radius: 4, x: 0, y: 2)
        )
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .stroke(Color(.systemGray4), lineWidth: 1)
        )
        .padding(.horizontal)
    }
    
    // Helper function to convert string color to SwiftUI Color
    private func colorFromString(_ colorString: String) -> Color {
        switch colorString.lowercased() {
        case "green":
            return .green
        case "orange":
            return .orange
        case "red":
            return .red
        case "blue":
            return .blue
        default:
            return .primary
        }
    }
    
    // Helper to parse measurement summary for comparison display
    private func parseMeasurementSummary(_ summary: String) -> [MeasurementComparison] {
        // Simple parsing - in real implementation would parse the actual summary
        return [
            MeasurementComparison(dimension: "chest", value: "42", userRange: "40-44"),
            MeasurementComparison(dimension: "neck", value: "16", userRange: "15.5-16.5")
        ]
    }
}

// Helper struct for measurement comparison
// RangeComparisonDetails removed - no longer needed with new DimensionComparison structure

#Preview {
    ScanTab()
}
