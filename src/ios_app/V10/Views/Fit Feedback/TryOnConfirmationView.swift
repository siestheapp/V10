// TryOnConfirmationView.swift
// Handles try-on session confirmation and size selection before feedback.
// Replaces the deleted ProductConfirmationView for TryOnSession flow.

import SwiftUI

// J.Crew-style fit description modifier (matching their exact CSS)
struct JCrewFitDescriptionStyle: ViewModifier {
    let isSelected: Bool
    let fitType: String
    
    func body(content: Content) -> some View {
        HStack(spacing: 12) {
            // J.Crew official fit type image
            AsyncImage(url: URL(string: "https://www.jcrew.com/next-static/images/fit-types/SHIRTS_FIT_\(fitType).png")) { image in
                image
                    .resizable()
                    .aspectRatio(contentMode: .fit)
            } placeholder: {
                // Fallback icon if image doesn't load
                Image(systemName: "tshirt")
                    .foregroundColor(.gray)
            }
            .frame(width: 40, height: 40)
            
            // Description text
            content
                .font(.system(size: 13, weight: .regular)) // .8125rem = 13px
                .foregroundColor(Color.black) // #000
                .kerning(0.3) // letter-spacing: .3px
                .lineSpacing(13 * 0.4) // line-height: 1.4
                .multilineTextAlignment(.leading) // justify-content: left
                .frame(maxWidth: .infinity, alignment: .leading)
        }
        .padding(8) // .5rem = 8px
        .background(
            RoundedRectangle(cornerRadius: 5) // border-radius: 5px
                .fill(Color(red: 245/255, green: 245/255, blue: 245/255, opacity: 0.502)) // rgba(245,245,245,.5019607843)
                .overlay(
                    RoundedRectangle(cornerRadius: 5)
                        .stroke(Color(red: 190/255, green: 190/255, blue: 190/255), lineWidth: 1) // 1px solid #bebebe
                )
        )
    }
}

struct TryOnConfirmationView: View {
    let session: TryOnSession
    @State private var selectedSize: String = ""
    @State private var selectedFit: String = ""
    @State private var selectedColor: String = ""
    @State private var navigateToFeedback = false
    @State private var displayedProductName: String = ""
    @State private var displayedColorOptions: [JCrewColor] = []
    
    // Get fit options from session data
    private var availableFitOptions: [String] {
        return session.fitOptions.isEmpty ? [] : session.fitOptions
    }
    
    // Get color options from session data (rich objects)
    private var availableColorOptions: [JCrewColor] {
        return displayedColorOptions.isEmpty ? session.colorOptions : displayedColorOptions
    }
    
    // Computed property to determine if Continue button should be disabled
    private var isDisabled: Bool {
        var requirements: [Bool] = [!selectedSize.isEmpty]
        
        if !availableFitOptions.isEmpty {
            requirements.append(!selectedFit.isEmpty)
        }
        
        // For single color, it's auto-selected, but for multiple colors user must select
        if availableColorOptions.count > 1 {
            requirements.append(!selectedColor.isEmpty)
        }
        
        return !requirements.allSatisfy { $0 }
    }
    
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Product Image - LARGE like real ecommerce apps
                if !session.productImage.isEmpty {
                    AsyncImage(url: URL(string: session.productImage)) { image in
                        image
                            .resizable()
                            .aspectRatio(contentMode: .fit)
                    } placeholder: {
                        Rectangle()
                            .fill(Color.gray.opacity(0.1))
                            .aspectRatio(1, contentMode: .fit) // Square placeholder
                            .overlay(
                                ProgressView()
                            )
                    }
                    // Full width, let image determine its own height
                    .frame(maxWidth: .infinity)
                    // No fixed height - image maintains its natural aspect ratio
                    // No background color - removes grey padding
                }
                
                VStack(spacing: 20) {
                    // Product Info (compact, below image)
                    VStack(spacing: 6) {
                        Text(session.brand)
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .textCase(.uppercase)
                            .tracking(1.2)
                        
                        Text(displayedProductName.isEmpty ? session.productName : displayedProductName)
                            .font(.title3)
                            .fontWeight(.semibold)
                            .multilineTextAlignment(.center)
                    }
                    .padding(.horizontal)
                
                // Fit Selection (for products with fit options)
                if !availableFitOptions.isEmpty {
                    VStack(alignment: .leading, spacing: 16) {
                        Text("Select Fit Type")
                            .font(.headline)
                            .fontWeight(.bold)
                        
                        Text("Which fit are you trying on? This affects the measurements.")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                        
                        VStack(spacing: 16) {
                            // Fit option buttons
                            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 3), spacing: 12) {
                                ForEach(availableFitOptions, id: \.self) { fit in
                                    Button(action: {
                                        print("🔍 Fit button tapped: '\(fit)'")
                                        selectedFit = fit
                                        print("🔍 Selected fit is now: '\(selectedFit)'")
                                        
                                        // Only update colors based on fit variation (not product name)
                                        if let fitVariations = session.fitVariations,
                                           let fitData = fitVariations[fit] {
                                            // Update available colors (fitData.colorsAvailable is already [JCrewColor])
                                            displayedColorOptions = fitData.colorsAvailable
                                            print("🎨 Updated colors: \(displayedColorOptions.count) colors available for \(fit) fit")
                                            
                                            // Reset color selection if current color is not in new options
                                            if !selectedColor.isEmpty && !displayedColorOptions.contains(where: { $0.name == selectedColor }) {
                                                selectedColor = ""
                                                print("⚠️ Reset color selection - not available in new fit")
                                            }
                                        }
                                    }) {
                                        Text(fit)
                                            .font(.subheadline)
                                            .fontWeight(.medium)
                                            .foregroundColor(selectedFit == fit ? .white : .primary)
                                            .frame(maxWidth: .infinity)
                                            .padding(.vertical, 12)
                                            .padding(.horizontal, 8)
                                            .background(
                                                RoundedRectangle(cornerRadius: 8)
                                                    .fill(selectedFit == fit ? Color.blue : Color(.systemGray5))
                                            )
                                    }
                                }
                            }
                            
                            // J.Crew-style fit description with official images (shows only for selected fit)
                            if !selectedFit.isEmpty {
                                if selectedFit == "Tall" {
                                    Text("2\" longer in the body and sleeves compared to our Classic fit.")
                                        .modifier(JCrewFitDescriptionStyle(isSelected: true, fitType: "Tall"))
                                } else if selectedFit == "Slim" {
                                    Text("Tapered fit through the body and sleeves.")
                                        .modifier(JCrewFitDescriptionStyle(isSelected: true, fitType: "Slim"))
                                } else if selectedFit == "Classic" {
                                    Text("Our signature fit with a comfortable, time-tested cut.")
                                        .modifier(JCrewFitDescriptionStyle(isSelected: true, fitType: "Classic"))
                                } else if selectedFit == "Relaxed" {
                                    Text("Roomier fit through the body for added comfort.")
                                        .modifier(JCrewFitDescriptionStyle(isSelected: true, fitType: "Relaxed"))
                                }
                            }
                        }
                    }
                    .padding()
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(Color(.systemBackground))
                            .shadow(color: .black.opacity(0.1), radius: 2, x: 0, y: 1)
                    )
                }
                
                // Color Selection (show even for single color for clarity)
                if !availableColorOptions.isEmpty {
                    VStack(alignment: .leading, spacing: 16) {
                        Text(availableColorOptions.count > 1 ? "Select Color" : "Color")
                            .font(.headline)
                            .fontWeight(.bold)
                        
                        Text(availableColorOptions.count > 1 ? "Which color are you trying on?" : "You're trying on:")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                        
                        // Show selected color name
                        if !selectedColor.isEmpty {
                            Text(selectedColor)
                                .font(.system(size: 14, weight: .medium))
                                .foregroundColor(.primary)
                                .padding(.horizontal, 12)
                                .padding(.vertical, 6)
                                .background(
                                    RoundedRectangle(cornerRadius: 6)
                                        .fill(Color(.systemGray6))
                                )
                        }
                        
                        // Grid of circular swatches (no labels)
                        LazyVGrid(columns: [GridItem(.adaptive(minimum: 44), spacing: 12)], spacing: 12) {
                            ForEach(availableColorOptions, id: \.self) { color in
                                Button(action: {
                                    // Only allow selection if there are multiple colors
                                    if availableColorOptions.count > 1 {
                                        print("🎨 Color swatch tapped: '\(color.name)'")
                                        selectedColor = color.name
                                    }
                                }) {
                                    swatchView(for: color)
                                        .frame(width: 44, height: 44)
                                        .overlay(
                                            Circle()
                                                .stroke(selectedColor == color.name ? Color.blue : Color.gray.opacity(0.3), lineWidth: selectedColor == color.name ? 3 : 1)
                                        )
                                }
                                .buttonStyle(PlainButtonStyle())
                                .disabled(availableColorOptions.count == 1) // Disable if only one color
                            }
                        }
                    }
                    .padding()
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(Color(.systemBackground))
                            .shadow(color: .black.opacity(0.1), radius: 2, x: 0, y: 1)
                    )
                }
                
                // Size Selection - Dressing Room Experience
                VStack(alignment: .leading, spacing: 16) {
                    Text("What Size Are You Trying On?")
                        .font(.headline)
                        .fontWeight(.bold)
                    
                    Text("Select the size on the tag you're about to try on")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                    
                    LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 3), spacing: 12) {
                        ForEach(session.sizeOptions, id: \.self) { size in
                            Button(action: {
                                print("🔍 Size button tapped: '\(size)'")
                                selectedSize = size
                                print("🔍 Selected size is now: '\(selectedSize)'")
                            }) {
                                Text(size)
                                    .font(.headline)
                                    .foregroundColor(selectedSize == size ? .white : .primary)
                                    .frame(maxWidth: .infinity)
                                    .padding()
                                    .background(
                                        RoundedRectangle(cornerRadius: 8)
                                            .fill(selectedSize == size ? Color.blue : Color(.systemGray5))
                                    )
                            }
                        }
                    }
                }
                .padding()
                .background(
                    RoundedRectangle(cornerRadius: 12)
                        .fill(Color(.systemBackground))
                        .shadow(color: .black.opacity(0.1), radius: 2, x: 0, y: 1)
                )
                
                // Continue Button - At bottom for better UX flow
                Button(action: {
                    print("🔍 Continue button tapped")
                    print("🔍 Selected size: '\(selectedSize)'")
                    print("🔍 Selected fit: '\(selectedFit)'")
                    print("🔍 Is J.Crew: \(session.brand.lowercased() == "j.crew")")
                    navigateToFeedback = true
                }) {
                    Text("Continue")
                        .font(.headline)
                        .fontWeight(.semibold)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 16)
                        .background(
                            RoundedRectangle(cornerRadius: 12)
                                .fill(isDisabled ? Color.gray : Color.blue)
                        )
                }
                .disabled(isDisabled)
                .padding(.horizontal)
                .padding(.bottom, 20)
                .onAppear {
                    print("🔍 Continue button appeared - selectedSize: '\(selectedSize)', selectedFit: '\(selectedFit)', disabled: \(isDisabled)")
                }
                
                }  // End of inner VStack
            }
            .padding()
        }
        .navigationTitle("Confirm Try-On")
        .navigationBarTitleDisplayMode(.inline)
        .sheet(isPresented: $navigateToFeedback) {
            NavigationView {
                FitFeedbackViewWithPhoto(
                    feedbackType: .manualEntry,
                    selectedSize: selectedSize,
                    productUrl: session.productUrl,
                    brand: session.brand,
                    fitType: selectedFit.isEmpty ? nil : selectedFit,
                    selectedColor: selectedColor.isEmpty ? nil : selectedColor
                )
            }
        }
        .onAppear {
            print("🔍 TryOnConfirmationView appeared")
            print("🔍 Session size options: \(session.sizeOptions)")
            print("🔍 Session fit options: \(session.fitOptions)")
            print("🔍 Available fit options: \(availableFitOptions)")
            print("🔍 Fit options count: \(availableFitOptions.count)")
            
            // Initialize displayed values from session
            // Use base product name (without fit prefix) like J.Crew app
            displayedProductName = session.baseProductName ?? session.productName
            
            // Always default to Classic fit like J.Crew app
            selectedFit = "Classic"
            print("🔍 Default to Classic fit (J.Crew standard behavior)")
            
            // Set colors for Classic fit
            if let fitVariations = session.fitVariations,
               let classicData = fitVariations["Classic"] {
                displayedColorOptions = classicData.colorsAvailable
                print("🎨 Initialized with \(classicData.colorsAvailable.count) colors for Classic fit")
            } else {
                // Fallback to session colors if no fit variations
                displayedColorOptions = session.colorOptions
            }
            print("🔍 Available measurements: \(session.availableMeasurements)")
            print("🔍 Selected size: '\(selectedSize)'")
            
            // Debug each fit option
            for (index, fit) in availableFitOptions.enumerated() {
                print("🔍 Fit option [\(index)]: '\(fit)'")
            }
            
            // Auto-select first size if only one option
            if session.sizeOptions.count == 1 {
                selectedSize = session.sizeOptions.first ?? ""
                print("🔍 Auto-selected size: '\(selectedSize)'")
            }
            
            // Auto-select current color if specified in URL
            if !session.currentColor.isEmpty && availableColorOptions.contains(where: { $0.name == session.currentColor }) {
                selectedColor = session.currentColor
                print("🎨 Auto-selected current color: '\(selectedColor)'")
            }
            
            // Auto-select color if only one option
            if availableColorOptions.count == 1 {
                selectedColor = availableColorOptions.first?.name ?? ""
                print("🎨 Auto-selected single color: '\(selectedColor)'")
            }
        }
    }
    
    // MARK: - Swatch Rendering
    private func swatchView(for color: JCrewColor) -> some View {
        Group {
            if let urlString = color.imageUrl, let url = URL(string: urlString) {
                AsyncImage(url: url) { phase in
                    switch phase {
                    case .success(let image):
                        image
                            .resizable()
                            .scaledToFill()
                    case .failure(let error):
                        // Log error and show fallback
                        let _ = print("❌ Failed to load color swatch: \(error)")
                        Circle().fill(colorFromHexOrName(color))
                    case .empty:
                        // Loading state
                        Circle().fill(Color.gray.opacity(0.3))
                    @unknown default:
                        Circle().fill(colorFromHexOrName(color))
                    }
                }
                .clipShape(Circle())
            } else {
                Circle().fill(colorFromHexOrName(color))
            }
        }
        .onAppear {
            if let url = color.imageUrl {
                print("🎨 Loading swatch for \(color.name): \(url)")
            } else {
                print("⚠️ No imageUrl for color: \(color.name)")
            }
        }
    }
    
    private func colorFromHexOrName(_ color: JCrewColor) -> Color {
        if let hex = color.hex, let uiColor = UIColor(hex: hex) {
            return Color(uiColor)
        }
        return colorForFallbackName(color.name)
    }
    
    // Fallback mapping by name for when hex is unavailable - using J.Crew's exact color palette
    private func colorForFallbackName(_ colorName: String) -> Color {
        let name = colorName.lowercased()
        
        // J.Crew specific color mappings based on their actual color names and hex values
        switch name {
        // Whites & Creams
        case "white", "ivory":
            return Color(UIColor(red: 255/255, green: 255/255, blue: 255/255, alpha: 1.0))
        case "natural", "cream", "off-white":
            return Color(UIColor(red: 235/255, green: 225/255, blue: 210/255, alpha: 1.0))
            
        // Blacks & Grays
        case "black", "charcoal":
            return Color(UIColor(red: 33/255, green: 33/255, blue: 33/255, alpha: 1.0))
        case "gray", "grey", "heather gray":
            return Color(UIColor(red: 150/255, green: 150/255, blue: 150/255, alpha: 1.0))
            
        // Blues
        case "navy", "navy blue":
            return Color(UIColor(red: 26/255, green: 42/255, blue: 68/255, alpha: 1.0))
        case "blue", "classic blue":
            return Color(UIColor(red: 70/255, green: 130/255, blue: 180/255, alpha: 1.0))
        case "light blue", "sky blue":
            return Color(UIColor(red: 173/255, green: 216/255, blue: 230/255, alpha: 1.0))
        case "deep spearmint":
            return Color(UIColor(red: 62/255, green: 180/255, blue: 137/255, alpha: 1.0))
            
        // Greens
        case "jcrew green", "j.crew green", "dark green", "forest green":
            return Color(UIColor(red: 40/255, green: 65/255, blue: 50/255, alpha: 1.0))
        case "misty sage", "sage", "sage green":
            return Color(UIColor(red: 155/255, green: 170/255, blue: 150/255, alpha: 1.0))
        case "alhambra green", "teal green", "emerald":
            return Color(UIColor(red: 80/255, green: 140/255, blue: 120/255, alpha: 1.0))
        case "olive", "olive green":
            return Color(UIColor(red: 107/255, green: 114/255, blue: 69/255, alpha: 1.0))
            
        // Browns
        case "inky mocha", "mocha", "dark brown":
            return Color(UIColor(red: 60/255, green: 45/255, blue: 40/255, alpha: 1.0))
        case "brown", "chocolate":
            return Color(UIColor(red: 101/255, green: 67/255, blue: 33/255, alpha: 1.0))
        case "tan", "camel", "khaki":
            return Color(UIColor(red: 195/255, green: 176/255, blue: 145/255, alpha: 1.0))
        case "burnt mushroom":
            return Color(UIColor(red: 139/255, green: 115/255, blue: 85/255, alpha: 1.0))
            
        // Reds & Pinks
        case "red", "classic red":
            return Color(UIColor(red: 200/255, green: 30/255, blue: 30/255, alpha: 1.0))
        case "burgundy", "wine", "maroon":
            return Color(UIColor(red: 128/255, green: 0/255, blue: 32/255, alpha: 1.0))
        case "pink", "rose", "blush":
            return Color(UIColor(red: 255/255, green: 192/255, blue: 203/255, alpha: 1.0))
        case "dusty pink", "mauve":
            return Color(UIColor(red: 183/255, green: 132/255, blue: 167/255, alpha: 1.0))
        case "fuchsia berry", "fuchsia":
            return Color(UIColor(red: 204/255, green: 57/255, blue: 123/255, alpha: 1.0))
            
        // Purples
        case "purple", "plum":
            return Color(UIColor(red: 128/255, green: 0/255, blue: 128/255, alpha: 1.0))
        case "lavender":
            return Color(UIColor(red: 230/255, green: 230/255, blue: 250/255, alpha: 1.0))
            
        // Yellows & Oranges
        case "yellow", "gold":
            return Color(UIColor(red: 255/255, green: 215/255, blue: 0/255, alpha: 1.0))
        case "orange", "rust":
            return Color(UIColor(red: 255/255, green: 140/255, blue: 0/255, alpha: 1.0))
            
        // Special J.Crew Colors
        case "heather", "heathered":
            return Color(UIColor(red: 156/255, green: 156/255, blue: 166/255, alpha: 1.0))
        case "stripe", "striped":
            return Color(UIColor(red: 200/255, green: 200/255, blue: 200/255, alpha: 1.0))
            
        default:
            return Color.gray.opacity(0.5)
        }
    }
}

extension UIColor {
    convenience init?(hex: String) {
        var cleaned = hex.trimmingCharacters(in: .whitespacesAndNewlines)
        if cleaned.hasPrefix("#") { cleaned.removeFirst() }
        guard cleaned.count == 6, let value = Int(cleaned, radix: 16) else { return nil }
        let r = CGFloat((value >> 16) & 0xFF) / 255.0
        let g = CGFloat((value >> 8) & 0xFF) / 255.0
        let b = CGFloat(value & 0xFF) / 255.0
        self.init(red: r, green: g, blue: b, alpha: 1.0)
    }
}

//#Preview {
//    NavigationView {
//        TryOnConfirmationView(session: TryOnSession(
//            sessionId: "test-123",
//            brand: "J.Crew",
//            brandId: 1,
//            productName: "Vintage-wash cotton pocket T-shirt",
//            productUrl: "https://example.com/shirt",
//            productImage: "",
//            availableMeasurements: ["Chest", "Neck", "Sleeve"],
//            feedbackOptions: [],
//            sizeOptions: ["S", "M", "L", "XL"],
//            fitOptions: ["Classic", "Slim", "Tall"],
//            colorOptions: [
//                JCrewColor(name: "White", imageUrl: nil, hex: "#FFFFFF"),
//                JCrewColor(name: "Navy", imageUrl: nil, hex: "#1A2A44"),
//                JCrewColor(name: "Black", imageUrl: nil, hex: "#000000")
//            ],
//            currentColor: "White",
//            nextStep: "Try on the garment and provide feedback on how it fits."
//        ))
//    }
//}
