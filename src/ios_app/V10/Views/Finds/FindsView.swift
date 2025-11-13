import SwiftUI

struct FindsView: View {
    @State private var selectedTab: FindsTab = .all
    
    enum FindsTab: String, CaseIterable {
        case all = "All"
        case tryOns = "Try-Ons"
        
        var icon: String {
            switch self {
            case .all:
                return "list.bullet"
            case .tryOns:
                return "tshirt"
            }
        }
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Tab Pills
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 12) {
                    ForEach(FindsTab.allCases, id: \.self) { tab in
                        TabPill(
                            title: tab.rawValue,
                            icon: tab.icon,
                            isSelected: selectedTab == tab
                        ) {
                            selectedTab = tab
                        }
                    }
                }
                .padding(.horizontal)
            }
            .padding(.vertical, 12)
            .background(Color(.systemBackground))
            
            // Content
            TabView(selection: $selectedTab) {
                AllFindsView()
                    .tag(FindsTab.all)
                
                TryOnHistoryView()
                    .tag(FindsTab.tryOns)
            }
            .tabViewStyle(PageTabViewStyle(indexDisplayMode: .never))
        }
        .navigationTitle("Finds")
        .navigationBarTitleDisplayMode(.large)
    }
}

struct TabPill: View {
    let title: String
    let icon: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.subheadline)
                    .fontWeight(.medium)
                Text(title)
                    .font(.subheadline)
                    .fontWeight(.semibold)
            }
            .padding(.horizontal, 20)
            .padding(.vertical, 12)
            .background(
                Group {
                    if isSelected {
                        LinearGradient(colors: [.blue, .blue.opacity(0.8)], startPoint: .topLeading, endPoint: .bottomTrailing)
                    } else {
                        LinearGradient(colors: [Color(.systemGray6)], startPoint: .topLeading, endPoint: .bottomTrailing)
                    }
                }
            )
            .foregroundColor(
                isSelected ? .white : .primary
            )
            .clipShape(Capsule())
            .shadow(color: isSelected ? .blue.opacity(0.3) : .clear, radius: 8, x: 0, y: 2)
        }
        .buttonStyle(PlainButtonStyle())
        .scaleEffect(isSelected ? 1.02 : 1.0)
        .animation(.easeInOut(duration: 0.2), value: isSelected)
    }
}

#Preview {
    NavigationView {
        FindsView()
    }
}

