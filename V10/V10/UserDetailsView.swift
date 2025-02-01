import SwiftUI

struct UserDetailsView: View {
    var goBack: () -> Void
    @State private var selectedCategory: String?
    @State private var showMeasurementIntro = false
    
    var body: some View {
        if showMeasurementIntro {
            MeasurementIntroView()
        } else {
            ZStack(alignment: .topLeading) {
                Button(action: goBack) {
                    Image(systemName: "chevron.left")
                        .font(.title2)
                        .foregroundColor(.blue)
                        .padding()
                }
                
                VStack(spacing: 30) {
                    Text("Almost there!")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                    
                    VStack(alignment: .leading, spacing: 15) {
                        Text("Primary Clothing Category")
                            .font(.headline)
                        
                        HStack(spacing: 15) {
                            CategoryButton(title: "Womens", 
                                        isSelected: selectedCategory == "Womens",
                                        action: { selectedCategory = "Womens" })
                            
                            CategoryButton(title: "Mens", 
                                        isSelected: selectedCategory == "Mens",
                                        action: { selectedCategory = "Mens" })
                        }
                    }
                    .padding(.horizontal, 40)
                    
                    if let category = selectedCategory {
                        Button(action: {
                            print("Selected category: \(category)")
                            withAnimation {
                                showMeasurementIntro = true
                            }
                        }) {
                            Text("Continue")
                                .font(.headline)
                                .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.blue)
                                .cornerRadius(10)
                        }
                        .padding(.horizontal, 40)
                        .transition(.opacity)
                    }
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            }
            .background(Color(.systemBackground))
        }
    }
}

struct UserDetailsView_Previews: PreviewProvider {
    static var previews: some View {
        UserDetailsView(goBack: {})
    }
}

// Helper view for category buttons
struct CategoryButton: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.headline)
                .foregroundColor(isSelected ? .white : .blue)
                .frame(maxWidth: .infinity)
                .padding()
                .background(isSelected ? Color.blue : Color.white)
                .cornerRadius(10)
                .overlay(
                    RoundedRectangle(cornerRadius: 10)
                        .stroke(Color.blue, lineWidth: 1)
                )
        }
    }
} 
