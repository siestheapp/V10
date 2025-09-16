import SwiftUI

// PROPERLY OPTIMIZED: All features, but with correct performance patterns
struct ProperlyOptimizedScanTab: View {
    // OPTIMIZATION 1: Group related state into single objects
    @StateObject private var viewModel = ScanTabViewModel()
    @StateObject private var navigationState = ScanTabNavigationState()
    
    // OPTIMIZATION 2: Only essential UI state at view level
    @FocusState private var isTextFieldFocused: Bool
    @State private var selectedMode: ScanMode = .tryOn
    
    enum ScanMode: String, CaseIterable {
        case tryOn = "Try-On"
        case recommendation = "Size Check"
        
        var icon: String {
            self == .tryOn ? "tshirt.fill" : "magnifyingglass"
        }
    }
    
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {
                    headerSection
                    modeSelectorSection
                    scanSection
                    dividerSection
                    manualEntrySection
                }
                .padding(.vertical)
            }
            .navigationTitle("Scan")
            .navigationBarTitleDisplayMode(.inline)
            .sheet(item: $navigationState.activeSheet) { sheet in
                sheetContent(for: sheet)
            }
            .navigationDestination(isPresented: $navigationState.showingFitFeedback) {
                FitFeedbackView(
                    feedbackType: .manualEntry,
                    selectedSize: viewModel.selectedSize,
                    productUrl: viewModel.productLink,
                    brand: viewModel.brand
                )
            }
            .navigationDestination(isPresented: $navigationState.showingTryOnSession) {
                if let garment = viewModel.scannedGarment {
                    TryOnSessionView(
                        garment: garment,
                        productUrl: viewModel.productLink,
                        tryOnSession: viewModel.tryOnSession
                    )
                }
            }
        }
        // OPTIMIZATION 3: Load data ONLY when actually needed
        .task {
            await viewModel.initializeIfNeeded()
        }
    }
    
    // OPTIMIZATION 4: Extract sections as computed properties
    private var headerSection: some View {
        VStack(spacing: 12) {
            Image(systemName: "barcode.viewfinder")
                .font(.system(size: 48))
                .foregroundStyle(.blue)
            
            Text("Find Your Perfect Fit")
                .font(.title)
                .fontWeight(.bold)
            
            Text("Scan a tag or paste a product link")
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
        .padding(.top, 20)
    }
    
    private var modeSelectorSection: some View {
        // OPTIMIZATION 5: Pre-calculate expensive values
        HStack(spacing: 12) {
            ForEach(ScanMode.allCases, id: \.self) { mode in
                ModeSelectorButton(
                    mode: mode,
                    isSelected: selectedMode == mode,
                    action: { selectedMode = mode }
                )
            }
        }
        .padding(.horizontal, 20)
    }
    
    private var scanSection: some View {
        Button(action: { navigationState.activeSheet = .scanOptions }) {
            HStack(spacing: 16) {
                Image(systemName: "camera.fill")
                    .font(.title2)
                    .foregroundColor(.white)
                    .frame(width: 50, height: 50)
                    .background(Circle().fill(Color.blue))
                
                VStack(alignment: .leading, spacing: 4) {
                    Text("Scan a Tag")
                        .font(.headline)
                    Text("Use camera to scan garment tag")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.title3)
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(Color(.systemGray6))
            .cornerRadius(16)
        }
        .buttonStyle(PlainButtonStyle())
        .padding(.horizontal, 20)
    }
    
    private var dividerSection: some View {
        HStack {
            Rectangle()
                .fill(Color.gray.opacity(0.3))
                .frame(height: 1)
            
            Text("OR")
                .font(.caption)
                .fontWeight(.medium)
                .foregroundColor(.secondary)
                .padding(.horizontal, 12)
            
            Rectangle()
                .fill(Color.gray.opacity(0.3))
                .frame(height: 1)
        }
        .padding(.horizontal, 40)
    }
    
    private var manualEntrySection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Paste Product Link")
                .font(.headline)
                .padding(.horizontal, 20)
            
            HStack(spacing: 12) {
                // OPTIMIZATION 6: Simple text field without heavy modifiers
                TextField("Enter product URL", text: $viewModel.productLink)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .focused($isTextFieldFocused)
                    .onSubmit { analyzeIfReady() }
                
                if !viewModel.productLink.isEmpty {
                    Button(action: { viewModel.productLink = "" }) {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.secondary)
                    }
                }
            }
            .padding(.horizontal, 20)
            
            if !viewModel.productLink.isEmpty {
                Button(action: analyzeIfReady) {
                    HStack {
                        if viewModel.isAnalyzing {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                .scaleEffect(0.8)
                        } else {
                            Text(buttonText)
                                .fontWeight(.semibold)
                        }
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(12)
                }
                .disabled(viewModel.isAnalyzing)
                .padding(.horizontal, 20)
            }
            
            if let error = viewModel.analysisError {
                ErrorView(message: error) {
                    viewModel.analysisError = nil
                }
                .padding(.horizontal, 20)
            }
        }
    }
    
    private var buttonText: String {
        selectedMode == .tryOn ? "Start Try-On Session" : "Get Size Recommendation"
    }
    
    private func analyzeIfReady() {
        guard !viewModel.productLink.isEmpty else { return }
        
        Task {
            if selectedMode == .tryOn {
                await viewModel.startTryOnSession()
                // Check if we have a garment to start try-on with
                if viewModel.scannedGarment != nil {
                    navigationState.showingTryOnSession = true
                }
            } else {
                await viewModel.analyzeSizeRecommendation()
                if viewModel.sizeRecommendation != nil {
                    navigationState.activeSheet = .sizeRecommendation
                }
            }
        }
    }
    
    @ViewBuilder
    private func sheetContent(for sheet: ScanTabNavigationState.SheetType) -> some View {
        switch sheet {
        case .scanOptions:
            ScanOptionsSheet(
                onScanTag: {
                    navigationState.activeSheet = nil
                    navigationState.activeSheet = .scanner
                },
                onPickImage: {
                    navigationState.activeSheet = nil
                    navigationState.activeSheet = .imagePicker
                }
            )
        case .scanner:
            ScanGarmentView(
                selectedImage: viewModel.selectedImage,
                isPresented: .constant(true)
            )
        case .imagePicker:
            ImagePicker(image: $viewModel.selectedImage)
        case .sizeRecommendation:
            if let recommendation = viewModel.sizeRecommendation {
                SizeRecommendationScreen(recommendation: recommendation)
            }
        }
    }
}

// OPTIMIZATION 7: Extract complex components
struct ModeSelectorButton: View {
    let mode: ProperlyOptimizedScanTab.ScanMode
    let isSelected: Bool
    let action: () -> Void
    
    // OPTIMIZATION 8: Pre-compute colors instead of in body
    private var backgroundColor: Color {
        isSelected ? .blue : Color(.systemGray6)
    }
    
    private var foregroundColor: Color {
        isSelected ? .white : .primary
    }
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 8) {
                Image(systemName: mode.icon)
                    .font(.title2)
                Text(mode.rawValue)
                    .font(.caption)
                    .fontWeight(.medium)
            }
            .foregroundColor(foregroundColor)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 12)
            .background(RoundedRectangle(cornerRadius: 12).fill(backgroundColor))
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// OPTIMIZATION 9: Separate view model for business logic
@MainActor
class ScanTabViewModel: ObservableObject {
    @Published var productLink = ""
    @Published var isAnalyzing = false
    @Published var analysisError: String?
    @Published var sizeRecommendation: SizeRecommendationResponse?
    @Published var tryOnSession: TryOnSession?
    @Published var scannedGarment: Garment?
    @Published var userFitZones: ComprehensiveMeasurementData?
    @Published var selectedImage: UIImage?
    @Published var selectedSize = "M"
    @Published var brand: String?
    
    private var hasInitialized = false
    
    func initializeIfNeeded() async {
        guard !hasInitialized else { return }
        hasInitialized = true
        // Load any essential data here, but NOT fit zones until needed
    }
    
    func startTryOnSession() async {
        isAnalyzing = true
        analysisError = nil
        
        // In a real app, this would call your API
        // For now, create a mock garment for the try-on session
        scannedGarment = Garment(
            id: 1,
            brand: brand ?? "Unknown",
            productName: "Test Product",
            productUrl: productLink,
            imageUrl: nil,
            category: "Tops",
            sizeLabel: selectedSize,
            ownsGarment: false,
            fitFeedback: nil,
            feedbackTimestamp: nil
        )
        
        // The actual TryOnSession would be created by the backend
        // We'll let TryOnSessionView handle creating it
        
        isAnalyzing = false
    }
    
    func analyzeSizeRecommendation() async {
        isAnalyzing = true
        analysisError = nil
        
        // Load fit zones ONLY when actually analyzing
        if userFitZones == nil {
            await loadUserFitZones()
        }
        
        // Simulate API call
        try? await Task.sleep(nanoseconds: 1_500_000_000)
        
        // Mock recommendation
        // In real app, call your API here
        
        isAnalyzing = false
    }
    
    private func loadUserFitZones() async {
        // Load only when needed, not on view appear
        try? await Task.sleep(nanoseconds: 500_000_000)
        // Load actual data here
    }
}

// OPTIMIZATION 10: Separate navigation state
@MainActor
class ScanTabNavigationState: ObservableObject {
    enum SheetType: Identifiable {
        case scanOptions
        case scanner
        case imagePicker
        case sizeRecommendation
        
        var id: String { String(describing: self) }
    }
    
    @Published var activeSheet: SheetType?
    @Published var showingFitFeedback = false
    @Published var showingTryOnSession = false
}

// Simple error view component
struct ErrorView: View {
    let message: String
    let onDismiss: () -> Void
    
    var body: some View {
        HStack {
            Image(systemName: "exclamationmark.triangle")
                .foregroundColor(.orange)
            Text(message)
                .font(.caption)
                .foregroundColor(.secondary)
            Spacer()
            Button(action: onDismiss) {
                Image(systemName: "xmark.circle.fill")
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(Color.orange.opacity(0.1))
        .cornerRadius(8)
    }
}

// Placeholder sheets (implement your actual views)
struct ScanOptionsSheet: View {
    let onScanTag: () -> Void
    let onPickImage: () -> Void
    
    var body: some View {
        VStack(spacing: 20) {
            Button("Scan Tag", action: onScanTag)
            Button("Choose Photo", action: onPickImage)
        }
        .padding()
    }
}

