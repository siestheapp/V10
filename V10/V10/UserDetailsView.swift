import SwiftUI

struct UserDetailsView: View {
    var goBack: () -> Void
    @State private var selectedCategory: String?
    
    var body: some View {
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
                        Button(action: {
                            selectedCategory = "Womens"
                        }) {
                            Text("Womens")
                                .font(.headline)
                                .foregroundColor(selectedCategory == "Womens" ? .white : .blue)
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(selectedCategory == "Womens" ? Color.blue : Color.white)
                                .cornerRadius(10)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 10)
                                        .stroke(Color.blue, lineWidth: 1)
                                )
                        }
                        
                        Button(action: {
                            selectedCategory = "Mens"
                        }) {
                            Text("Mens")
                                .font(.headline)
                                .foregroundColor(selectedCategory == "Mens" ? .white : .blue)
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(selectedCategory == "Mens" ? Color.blue : Color.white)
                                .cornerRadius(10)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 10)
                                        .stroke(Color.blue, lineWidth: 1)
                                )
                        }
                    }
                }
                .padding(.horizontal, 40)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
        .background(Color(.systemBackground))
    }
} 
