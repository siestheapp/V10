import SwiftUI

struct CanvasView: View {
    @State private var canvasData: CanvasResponse?
    @State private var isLoading = true
    @State private var errorMessage: String?
    @State private var selectedSection: CanvasSection = .overview
    
    enum CanvasSection: String, CaseIterable {
        case overview = "Overview"
        case rawFeedback = "Raw Feedback"
        case bodyEstimates = "Body Estimates"
        case fitZones = "Fit Zones"
        case recommendations = "Recommendations"
        case algorithms = "Algorithm Details"
    }
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Section Picker
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 12) {
                        ForEach(CanvasSection.allCases, id: \.self) { section in
                            Button(action: {
                                selectedSection = section
                            }) {
                                Text(section.rawValue)
                                    .font(.subheadline)
                                    .fontWeight(.medium)
                                    .padding(.horizontal, 16)
                                    .padding(.vertical, 8)
                                    .background(selectedSection == section ? Color.blue : Color.gray.opacity(0.1))
                                    .foregroundColor(selectedSection == section ? .white : .primary)
                                    .cornerRadius(20)
                            }
                        }
                    }
                    .padding(.horizontal)
                }
                .padding(.vertical, 8)
                
                Divider()
                
                // Content
                if isLoading {
                    Spacer()
                    VStack {
                        ProgressView()
                        Text("Analyzing measurement data...")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .padding(.top)
                    }
                    Spacer()
                } else if let error = errorMessage {
                    Spacer()
                    VStack {
                        Image(systemName: "exclamationmark.triangle")
                            .font(.largeTitle)
                            .foregroundColor(.orange)
                        Text("Error Loading Canvas Data")
                            .font(.headline)
                            .padding(.top)
                        Text(error)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal)
                    }
                    Spacer()
                } else if let data = canvasData {
                    ScrollView {
                        LazyVStack(alignment: .leading, spacing: 20) {
                            switch selectedSection {
                            case .overview:
                                OverviewSection(data: data)
                            case .rawFeedback:
                                RawFeedbackSection(data: data)
                            case .bodyEstimates:
                                BodyEstimatesSection(data: data)
                            case .fitZones:
                                FitZonesSection(data: data)
                            case .recommendations:
                                RecommendationsSection(data: data)
                            case .algorithms:
                                AlgorithmDetailsSection(data: data)
                            }
                        }
                        .padding()
                    }
                }
            }
            .navigationTitle("Canvas")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Refresh") {
                        loadCanvasData()
                    }
                    .disabled(isLoading)
                }
            }
            .onAppear {
                loadCanvasData()
            }
        }
    }
    
    private func loadCanvasData() {
        isLoading = true
        errorMessage = nil
        
        // For now, use mock data for immediate testing
        // TODO: Replace with actual API call once backend is ready
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
            self.isLoading = false
            self.canvasData = CanvasResponse.mockData
        }
        
        // Uncomment below when backend is ready:
        /*
        guard let url = URL(string: "\(Config.baseURL)/canvas/user/\(Config.defaultUserId)") else {
            errorMessage = "Invalid URL"
            isLoading = false
            return
        }
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            DispatchQueue.main.async {
                isLoading = false
                
                if let error = error {
                    errorMessage = error.localizedDescription
                    return
                }
                
                guard let data = data else {
                    errorMessage = "No data received"
                    return
                }
                
                do {
                    canvasData = try JSONDecoder().decode(CanvasResponse.self, from: data)
                } catch {
                    errorMessage = "Failed to decode: \(error.localizedDescription)"
                    print("Canvas decode error: \(error)")
                }
            }
        }.resume()
        */
    }
}

// MARK: - Section Views

struct OverviewSection: View {
    let data: CanvasResponse
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            SectionHeader(title: "System Overview", icon: "chart.bar.fill")
            
            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: 16) {
                StatCard(
                    title: "Total Garments",
                    value: "\(data.summary.totalGarments)",
                    subtitle: "owned items",
                    color: .blue
                )
                
                StatCard(
                    title: "Feedback Entries", 
                    value: "\(data.summary.totalFeedback)",
                    subtitle: "across all dimensions",
                    color: .green
                )
                
                StatCard(
                    title: "Dimensions Tracked",
                    value: "\(data.summary.dimensionsWithData.count)",
                    subtitle: data.summary.dimensionsWithData.joined(separator: ", "),
                    color: .orange
                )
                
                StatCard(
                    title: "Confidence Score",
                    value: String(format: "%.0f%%", data.summary.overallConfidence * 100),
                    subtitle: "prediction accuracy",
                    color: .purple
                )
            }
            
            // Data Quality Indicators
            VStack(alignment: .leading, spacing: 12) {
                Text("Data Quality")
                    .font(.headline)
                
                ForEach(data.summary.dimensionsWithData, id: \.self) { dimension in
                    let dimensionData = data.rawFeedback.filter { $0.dimension == dimension }
                    let feedbackCount = dimensionData.count
                    let uniqueFeedbackTypes = Set(dimensionData.map { $0.feedbackText }).count
                    
                    HStack {
                        Text(dimension.capitalized)
                            .font(.subheadline)
                            .fontWeight(.medium)
                            .frame(width: 80, alignment: .leading)
                        
                        VStack(alignment: .leading, spacing: 2) {
                            HStack {
                                Text("\(feedbackCount) feedback entries")
                                    .font(.caption)
                                Spacer()
                                Text("\(uniqueFeedbackTypes) feedback types")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                            
                            ProgressView(value: min(Double(feedbackCount) / 10.0, 1.0))
                                .progressViewStyle(LinearProgressViewStyle(tint: qualityColor(for: feedbackCount)))
                        }
                    }
                    .padding(.vertical, 4)
                }
            }
            .padding()
            .background(Color(.systemGray6))
            .cornerRadius(12)
        }
    }
    
    private func qualityColor(for count: Int) -> Color {
        switch count {
        case 0...2: return .red
        case 3...5: return .orange
        case 6...9: return .yellow
        default: return .green
        }
    }
}

struct RawFeedbackSection: View {
    let data: CanvasResponse
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            SectionHeader(title: "Raw Feedback Data", icon: "text.bubble.fill")
            
            // Group by garment
            let groupedFeedback = Dictionary(grouping: data.rawFeedback) { $0.garmentId }
            
            ForEach(groupedFeedback.keys.sorted(), id: \.self) { garmentId in
                let feedback = groupedFeedback[garmentId] ?? []
                let firstFeedback = feedback.first!
                
                VStack(alignment: .leading, spacing: 12) {
                    // Garment Header
                    HStack {
                        VStack(alignment: .leading, spacing: 4) {
                            Text(firstFeedback.brand)
                                .font(.subheadline)
                                .fontWeight(.bold)
                                .foregroundColor(.blue)
                            Text(firstFeedback.productName)
                                .font(.caption)
                                .foregroundColor(.secondary)
                                .lineLimit(2)
                        }
                        
                        Spacer()
                        
                        Text("Size \(firstFeedback.sizeLabel)")
                            .font(.subheadline)
                            .fontWeight(.medium)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(Color.blue.opacity(0.1))
                            .cornerRadius(6)
                    }
                    
                    // Feedback by Dimension
                    LazyVGrid(columns: [
                        GridItem(.flexible()),
                        GridItem(.flexible())
                    ], spacing: 8) {
                        ForEach(feedback.sorted(by: { $0.dimension < $1.dimension }), id: \.id) { item in
                            HStack {
                                Text(item.dimension.capitalized)
                                    .font(.caption)
                                    .fontWeight(.medium)
                                    .frame(width: 50, alignment: .leading)
                                
                                Text(item.feedbackText)
                                    .font(.caption)
                                    .foregroundColor(feedbackColor(for: item.feedbackText))
                                    .padding(.horizontal, 6)
                                    .padding(.vertical, 2)
                                    .background(feedbackColor(for: item.feedbackText).opacity(0.1))
                                    .cornerRadius(4)
                                
                                Spacer()
                            }
                        }
                    }
                }
                .padding()
                .background(Color(.systemBackground))
                .cornerRadius(12)
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(Color(.systemGray4), lineWidth: 1)
                )
            }
        }
    }
    
    private func feedbackColor(for feedback: String) -> Color {
        switch feedback {
        case "Good Fit": return .green
        case "Tight but I Like It", "Too Tight": return .red
        case "Loose but I Like It", "Too Loose", "Slightly Loose": return .blue
        default: return .gray
        }
    }
}

struct BodyEstimatesSection: View {
    let data: CanvasResponse
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            SectionHeader(title: "Estimated Body Measurements", icon: "ruler.fill")
            
            if data.bodyEstimates.isEmpty {
                Text("No body measurement estimates available")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .italic()
            } else {
                ForEach(data.bodyEstimates, id: \.dimension) { estimate in
                    VStack(alignment: .leading, spacing: 12) {
                        HStack {
                            Text(estimate.dimension.capitalized)
                                .font(.headline)
                                .fontWeight(.bold)
                            
                            Spacer()
                            
                            VStack(alignment: .trailing, spacing: 2) {
                                Text(String(format: "%.1f\"", estimate.estimatedMeasurement))
                                    .font(.title2)
                                    .fontWeight(.bold)
                                    .foregroundColor(.blue)
                                Text("\(estimate.dataPoints) data points")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                        }
                        
                        // Confidence Indicator
                        HStack {
                            Text("Confidence:")
                                .font(.subheadline)
                            
                            ProgressView(value: estimate.confidence)
                                .progressViewStyle(LinearProgressViewStyle(tint: confidenceColor(for: estimate.confidence)))
                            
                            Text(String(format: "%.0f%%", estimate.confidence * 100))
                                .font(.subheadline)
                                .fontWeight(.medium)
                        }
                        
                        // Algorithm Details
                        Text("Algorithm: \(estimate.method)")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        
                        Text("Range: \(String(format: "%.1f\" - %.1f\"", estimate.confidenceRange.min, estimate.confidenceRange.max))")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    .padding()
                    .background(Color(.systemGray6))
                    .cornerRadius(12)
                }
            }
        }
    }
    
    private func confidenceColor(for confidence: Double) -> Color {
        switch confidence {
        case 0.8...1.0: return .green
        case 0.6..<0.8: return .orange
        default: return .red
        }
    }
}

struct FitZonesSection: View {
    let data: CanvasResponse
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            SectionHeader(title: "Calculated Fit Zones", icon: "target")
            
            if data.fitZones.isEmpty {
                Text("No fit zones calculated")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .italic()
            } else {
                ForEach(Array(data.fitZones.enumerated()), id: \.offset) { index, zone in
                    VStack(alignment: .leading, spacing: 12) {
                        Text("\(zone.dimension.capitalized) Fit Zones")
                            .font(.headline)
                            .fontWeight(.bold)
                        
                        // Zone Visualization
                        let fitZoneRanges = FitZoneRanges(
                            tightRange: CanvasMeasurementRange(min: zone.tightMin, max: zone.tightMax),
                            goodRange: CanvasMeasurementRange(min: zone.goodMin, max: zone.goodMax),
                            relaxedRange: CanvasMeasurementRange(min: zone.relaxedMin, max: zone.relaxedMax),
                            garments: []
                        )
                        
                        FitZoneBar(
                            label: zone.dimension.capitalized,
                            ranges: convertToCanvasDimensionData(fitZoneRanges)
                        )
                        
                        Text("Based on \(zone.dataPoints) feedback entries")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    .padding()
                    .background(Color(.systemGray6))
                    .cornerRadius(12)
                }
            }
        }
    }
    
    // Convert FitZoneRanges to DimensionData for FitZonesSection
    private func convertToCanvasDimensionData(_ fitZoneRanges: FitZoneRanges) -> DimensionData {
        return DimensionData(
            tightRange: MeasurementRange(min: fitZoneRanges.tightRange.min, max: fitZoneRanges.tightRange.max),
            goodRange: MeasurementRange(min: fitZoneRanges.goodRange.min, max: fitZoneRanges.goodRange.max),
            relaxedRange: MeasurementRange(min: fitZoneRanges.relaxedRange.min, max: fitZoneRanges.relaxedRange.max),
            garments: fitZoneRanges.garments.map { garment in
                GarmentData(
                    brand: garment.brand,
                    garmentName: garment.garmentName,
                    range: garment.chestRange ?? "",
                    value: garment.chestValue,
                    size: garment.size,
                    fitFeedback: garment.fitFeedback,
                    feedback: garment.feedback,
                    ownsGarment: true
                )
            }
        )
    }
}

// Using existing FitZoneBar from UserMeasurementProfileView.swift

struct RecommendationsSection: View {
    let data: CanvasResponse
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            SectionHeader(title: "Size Recommendation Logic", icon: "lightbulb.fill")
            
            Text("Coming soon: Live size recommendation testing")
                .font(.subheadline)
                .foregroundColor(.secondary)
                .italic()
        }
    }
}

struct AlgorithmDetailsSection: View {
    let data: CanvasResponse
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            SectionHeader(title: "Algorithm Details", icon: "cpu.fill")
            
            VStack(alignment: .leading, spacing: 12) {
                AlgorithmCard(
                    title: "Body Measurement Estimator",
                    description: "Converts garment feedback to estimated body measurements",
                    parameters: [
                        "Feedback Deltas: Too Tight (-2\"), Good Fit (0\"), Too Loose (+2\")",
                        "Ease Calculations: Regular fit (1.5\" ease), Tight fit (0.5\")",
                        "Confidence Weighting: Product-level (1.0), Category-level (0.8)"
                    ]
                )
                
                AlgorithmCard(
                    title: "Multi-Dimensional Fit Analyzer", 
                    description: "Analyzes fit across chest, neck, sleeve, waist dimensions",
                    parameters: [
                        "Dimensions: \(data.summary.dimensionsWithData.joined(separator: ", "))",
                        "Statistical Zones: Weighted standard deviation",
                        "Confidence Thresholds: Chest (0.9), Neck (0.7), Sleeve (0.8)"
                    ]
                )
                
                AlgorithmCard(
                    title: "Direct Garment Comparator",
                    description: "Compares new garments to user's existing ones",
                    parameters: [
                        "Range Comparison: Identical, Similar, Different",
                        "Similarity Scoring: Weighted by feedback quality",
                        "Multi-dimensional Analysis: All available dimensions"
                    ]
                )
            }
        }
    }
}

struct AlgorithmCard: View {
    let title: String
    let description: String
    let parameters: [String]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.subheadline)
                .fontWeight(.bold)
            
            Text(description)
                .font(.caption)
                .foregroundColor(.secondary)
            
            ForEach(parameters, id: \.self) { parameter in
                Text("• \(parameter)")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(8)
    }
}

// MARK: - Helper Views

struct SectionHeader: View {
    let title: String
    let icon: String
    
    var body: some View {
        HStack {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(.blue)
            Text(title)
                .font(.title2)
                .fontWeight(.bold)
        }
    }
}

struct StatCard: View {
    let title: String
    let value: String
    let subtitle: String
    let color: Color
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(title)
                    .font(.caption)
                    .foregroundColor(.secondary)
                Spacer()
            }
            
            Text(value)
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(color)
            
            Text(subtitle)
                .font(.caption2)
                .foregroundColor(.secondary)
                .lineLimit(2)
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
}

#Preview {
    CanvasView()
} 