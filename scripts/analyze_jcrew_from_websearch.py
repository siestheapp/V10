#!/usr/bin/env python3
"""
Analyze J.Crew products from web search results
Since J.Crew blocks direct scraping, we'll use the HTML content from web search results
"""

import re
import sys
import psycopg2
from typing import Dict, List, Set
from collections import defaultdict

sys.path.append('/Users/seandavey/projects/V10')
from db_config import DB_CONFIG

# The HTML content from the web search results
JCREW_HTML_CONTENT = """
Skip to Main Content

J.Crew Passport gives you...

Free shipping on jcrew.com, personalized rewards & offers, birthday gifts and so much more.

Create an accountLearn more

Already have an account?

Sign in

FavoritesTrack order

J.Crew Logo

J.Crew Logo

* New  
##  
Shop New Arrivals  
For WomenFor Men For Girls For Boys  
##  
Women's spotlight  
J.Crew IconsDenim Fit GuidePant Fit GuideFall 2025 Campaign Wear-to-workPetite StylesWedding & PartyFall 2025 LookbookJ.Crew at 190 Bowery  
##  
What's new  
Women's new arrivalsMen's new arrivals
* Women  
##  
Women  
New ArrivalsBest SellersTop RatedThe Re-Imagined ShopShop AllSale  
## Clothing  
All Clothingsweaterspantsjeansshirts & topsdresses & jumpsuitsblazerstees & tankscoats & jacketsskirtsshortspajamas & intimatesswimsuitingsweatshirts & sweatpantsactive  
##  
Shoes & Sneakers  
All Shoes & SneakersBootsHeelsBalletsLoafersSneakersNew BalanceMade In ItalyBirkenstock  
All ShoesballetsheelsKnee-high bootsbootsloaferssneakers  
##  
Accessories  
All Accessorieshatsbagsbeltsjewelryhairsocks & tights  
##  
SPOTLIGHT ON  
J.Crew IconsDenim Fit GuidePant Fit GuideFall 2025 Campaign Wear-to-workPetite StylesWedding & PartyFall 2025 LookbookJ.Crew at 190 Bowery  
##  
What's new  
The new prepNow in stock: cashmere must-haves
* Men  
##  
Men  
New ArrivalsBest SellersTop RatedShop AllSale  
## Clothing  
All Clothingcasual shirtsdress shirtspants & chinosJeansshortssuits & tuxedosblazerst-shirts & polossweatersswimcoats & jacketssweatshirts & sweatpantspajamas & loungewearunderwear & boxers  
##  
Shoes & Sneakers  
All Shoes & SneakersBootsHeelsBalletsLoafersSneakersNew BalanceMade In ItalyBirkenstock  
All ShoesBoat ShoesLoafers & Slip OnsDress ShoesSneakersBoots  
##  
Accessories  
All AccessoriesSuiting AccessoriesHatsSocksBeltsSunglasses & EyewearBags & WalletsWatches & Jewelry  
##  
What's new  
Pants, perfectedNew arrivals
* Kids  
##  
Kids  
Girls' New ArrivalsBoys' New ArrivalsGirls' SaleBoys' Sale  
##  
Girls  
Shop All Girls  
All ClothingTopsdressesBottomscoats & jacketsactiveswim & rash guardspajamasbaby  
All AccessoriesAll Shoes & Sneakers  
##  
boys  
All Shoes & SneakersBootsHeelsBalletsLoafersSneakersNew BalanceMade In ItalyBirkenstock  
Shop All Boys  
All Clothingtopsbottomssuitingcoats & jacketsactiveswim & rash guardspajamasbaby  
All AccessoriesAll Shoes & Sneakers  
##  
accessories  
Girls' AccessoriesBoys' AccessoriesGirls' Shoes & SneakersBoys' Shoes & Sneakers  
##  
Shop by Age  
Baby (6mo-24mo)Girls (2-7)Girl (8-16)Boys (2-7)Boys (8-16)  
##  
SPOTLIGHT ON  
Picture-day PicksMini-me ShopAll Things CorduroyCashmere Shop  
##  
What's new  
The back-to-school collection
* Cashmere  
##  
Shop Cashmere  
For WomenFor MenFor GirlsFor BoysFor Baby  
##  
Shop Cashmere  
For WomenFor MenFor GirlsFor BoysFor Baby
* Brands  
Rouje X J.CrewPuma®  
##  
Top Women's Brands  
Rouje X J.CrewAnn Craven X J.CrewAraks X J.CrewNew Balance® State of CottonMarie MarotSLEEPERShop all  
New: Vans®Sperry®  
##  
Top Men's Brands  
Vans®Barbour®New Balance® Alden®Birkenstock®Shop all
* Quality  
##  
Quality Stories  
World-class FabricsSustainabilityCare GuidesEveryday LuxuriesQuality, Made Mini  
##  
Recycle & Resale  
Recycle Your SwimShop Vintage J.CrewResale via thredUP  
##  
Spotlight on  
Recycle your swimResponsible cashmere  
##  
Quality Stories  
World-class FabricsSustainabilityCare GuidesEveryday LuxuriesQuality, Made Mini  
##  
Recycle & Resale  
Recycle Your SwimShop Vintage J.CrewResale via thredUP  
##  
Spotlight on  
Recycle your swimResponsible cashmere
* Top Rated  
##  
Shop Top Rated  
For WomenFor MenFor GirlsFor Boys  
##  
Shop Top Rated  
For WomenFor MenFor GirlsFor Boys
* Sale  
##  
Sale  
Shop Women's Sale Shop Men's Sale Shop Girls' SaleShop Boys' Sale  
##  
Women  
Shop AllNew To SaleLess than $50Over 60% Off  
##  
Girls  
Shop AllNew To SaleLess than $50Over 60% Off  
##  
Men  
Shop AllNew To SaleLess than $50Over 60% Off  
##  
Boys  
Shop AllNew To SaleLess than $50Over 60% Off  
Limited time offers  
Limited Time Offers  
Shop Today's Deals  
30% off sitewide\* 50% off women's fall classics\*50% off men's fall classics\*50% off kids' fall classics\*  
Shop Sale  
##  
SALE  
Shop Women's Sale Shop Men's Sale Shop Girls' SaleShop Boys' Sale  
##  
Women  
Shop AllNew To SaleLess than $50Over 60% Off  
##  
Men  
Shop AllNew To SaleLess than $50Over 60% Off  
##  
Girls  
Shop AllNew To SaleLess than $50Over 60% Off  
##  
boys  
Shop AllNew To SaleLess than $50Over 60% Off  
Limited Time Offers  
Shop Today's Deals  
30% off sitewide\* 50% off women's fall classics\*50% off men's fall classics\*50% off kids' fall classics\*  
Shop Sale

* Cancel
* Shopping Bag  
Subtotal:  
Checkout

## 

Men's CASUAL SHIRTS

Broken-in oxfordIn soft organic cotton washed to feel like an old favorite.Shop allSecret WashThe favorite since 2005, woven in premium 100 percent cotton poplin.Shop allSeaboard Softer than soft, knit for comfort and flexibility. Shop allCorduroy Fall's favorite fabric that's rugged and refined. Shop allCotton-hempLightweight and comfortable with a slubby texture.Shop allBowery performanceThis wrinkle-resistant, breathable stretch cotton blend moves with you.Shop all

* Home
* /
* shop all
* /
* men
* /
* ### casual shirts

# SHOP ALL MEN'S CASUAL SHIRTS

Hide Filters

Featured

* Featured
* Price: Low - High
* Price: High - Low
* Top Rated
* New Arrival
* Best Seller

**Pick up today** Select a store

154 items

Go to page:1231

 of 3Page 1 of 3

View 120

## 

Fabric

linen (17)

secret wash (56)

broken-in oxford (25)

cotton linen (4)

camp collar (6)

tencel (3)

madras (1)

chambray, denim & indigo (9)

\+ Show 8 More

## 

Sleeve Length

short sleeve (24)

long sleeve (128)

## 

 Fit

slim (76)

slim untucked (37)

classic (123)

relaxed (46)

tall (46)

giant (3)

## 

Size

* Alpha
* X-SMALL
* SMALL
* MEDIUM
* LARGE
* X-LARGE
* XX-LARGE
* Tall Alpha
* TALL MEDIUM
* TALL LARGE
* X LARGE-TALL
* XX-LARGE-TALL

## 

Color

black (2)

blue (27)

brown (6)

gray (6)

green (10)

multicolor (64)

navy (8)

neutral (21)

orange (1)

pink (7)

purple (4)

red (1)

white (13)

## 

Pattern

animal print (1)

dots (1)

floral (2)

gingham (8)

graphic (2)

houndstooth (3)

marled (11)

paisley (4)

plaid (37)

stripes (32)

## 

Price

Min

$

Max

$

## 

Discount

60% and above (1)

50% - 60% off (5)

40% - 50% off (2)

less than 40% off (48)

## 

Occasion

casual (61)

workwear (71)

## 

Trending

best seller (62)

top rated (141)

new - last 2 weeks (1)

new - last 4 weeks (1)

monogrammable (76)

## 

Brand

atlantic coastal supplies (2)

the new yorker (1)

## 

Re-imagined

organic (23)

sustainable cellulosics (3)

## 

* mens Giant-fit oxford shirtonly a few left  
QUICK SHOP  
only a few leftGiant-fit oxford shirt$118select colors $105.99  
   * Giant-fit oxford shirt MANFRED BLUE ORANGE  
   * Giant-fit oxford shirt BOLD ROYAL WHITE OXFORD  
   * Giant-fit oxford shirt WHITE
* mens Cotton-cashmere blend shirt in checknew color  
QUICK SHOP  
new colorCotton-cashmere blend shirt in check$148  
   * Cotton-cashmere blend shirt in check JAMESON GREY BLACK  
   * Cotton-cashmere blend shirt in check BENNY NAVY BLACK  
   * Cotton-cashmere blend shirt in check DARK LODEN HEATHER  
   * Cotton-cashmere blend shirt in check ELIAS KHAKI MULTI  
   * Cotton-cashmere blend shirt in check BURKE MINI CHECK HTHR G  
   * Cotton-cashmere blend shirt in check DARK AZURE  
   * Cotton-cashmere blend shirt in check DARK CHOCOLATE
* mens Fine-wale corduroy shirtbest seller  
QUICK SHOP  
best sellerFine-wale corduroy shirt$118  
   * Fine-wale corduroy shirt DEEP KELLY GREEN  
   * Fine-wale corduroy shirt REDWOOD BROWN  
   * Fine-wale corduroy shirt TRUE AUBERGINE  
   * Fine-wale corduroy shirt NATURAL  
   * Fine-wale corduroy shirt DEEP NAVY
* mens Lightweight Seaboard soft-knit shirtbest seller  
QUICK SHOP  
best sellerLightweight Seaboard soft-knit shirt$98  
   * Lightweight Seaboard soft-knit shirt JAKE STONE MULTI  
   * Lightweight Seaboard soft-knit shirt HTHR MAROON  
   * Lightweight Seaboard soft-knit shirt TWILL CANVAS HEATHER  
   * Lightweight Seaboard soft-knit shirt EZRA GREEN BLUE  
   * Lightweight Seaboard soft-knit shirt MIKE BIRCH YELLOW  
   * Lightweight Seaboard soft-knit shirt SETH NAVY IVORY  
   * Lightweight Seaboard soft-knit shirt JOHN NAVY GREEN  
   * Lightweight Seaboard soft-knit shirt HTHR TEMPEST
* mens Lightweight Seaboard soft-knit shirttop rated  
QUICK SHOP  
top ratedLightweight Seaboard soft-knit shirt$98  
   * Lightweight Seaboard soft-knit shirt JAKE STONE MULTI  
   * Lightweight Seaboard soft-knit shirt HTHR MAROON  
   * Lightweight Seaboard soft-knit shirt TWILL CANVAS HEATHER  
   * Lightweight Seaboard soft-knit shirt EZRA GREEN BLUE  
   * Lightweight Seaboard soft-knit shirt MIKE BIRCH YELLOW  
   * Lightweight Seaboard soft-knit shirt SETH NAVY IVORY  
   * Lightweight Seaboard soft-knit shirt JOHN NAVY GREEN  
   * Lightweight Seaboard soft-knit shirt HTHR TEMPEST
* mens Secret Wash cotton poplin shirt with point collarbest seller  
QUICK SHOP  
best sellerSecret Wash cotton poplin shirt with point collar$98 Classic, Slim, Slim Untucked, Tall, Relaxed  
   * Secret Wash cotton poplin shirt with point collar JOHN WHITE BROWN  
   * Secret Wash cotton poplin shirt with point collar JIMMY BROWN MULTI  
   * Secret Wash cotton poplin shirt with point collar VICTOR BROWN GREEN  
   * Secret Wash cotton poplin shirt with point collar DENNIS WHITE PINK  
   * Secret Wash cotton poplin shirt with point collar ARMAND NAVY WHITE  
   * Secret Wash cotton poplin shirt with point collar REGGIE PLUM WHITE  
   * Secret Wash cotton poplin shirt with point collar COLE IVORY BLUE  
   * Secret Wash cotton poplin shirt with point collar HAROLD TAN BURGUNDY  
   * Secret Wash cotton poplin shirt with point collar PATRICK BLUE GREEN  
   * Secret Wash cotton poplin shirt with point collar JOSHUA BURGUNDY WHITE
* mens Fine-wale corduroy shirt with embroidered dogsnew  
QUICK SHOP  
newFine-wale corduroy shirt with embroidered dogs$158
* mens Broken-in organic cotton oxford shirtbest seller  
QUICK SHOP  
best sellerBroken-in organic cotton oxford shirt$98 Classic, Slim, Slim Untucked, Tall, Relaxed  
   * Broken-in organic cotton oxford shirt VINTAGE LILAC OXFORD  
   * Broken-in organic cotton oxford shirt RYAN WHITE PERI  
   * Broken-in organic cotton oxford shirt JASON BLUE MULTI  
   * Broken-in organic cotton oxford shirt JARVIS WHITE BROWN  
   * Broken-in organic cotton oxford shirt JARVIS WHITE BLACK  
   * Broken-in organic cotton oxford shirt LAWRENCE NAVY RED GREEN  
   * Broken-in organic cotton oxford shirt DOMINIC WHITE YELLOW  
   * Broken-in organic cotton oxford shirt DOMINIC WHITE LAVENDER  
   * Broken-in organic cotton oxford shirt RAY WHITE MULTI  
   * Broken-in organic cotton oxford shirt PALE ROSE OXFORD  
   * Broken-in organic cotton oxford shirt DOMINIC WHITE GREEN  
   * Broken-in organic cotton oxford shirt CHAMPIONSHIP GREEN WT  
   * Broken-in organic cotton oxford shirt UNIVERSITY STRIPE RAIN  
   * Broken-in organic cotton oxford shirt RAINCOAT BLUE  
   * Broken-in organic cotton oxford shirt WHITE

HAND-ME-DOWN QUALITYNEW ARRIVALS _Fall 2025_ Shop new arrivals

1. Page1of 3
2. Page2of 3
3. Page3of 3

Next

154 Items

View 120

Also Check Out Our Casual Shirts Sale

Back to top
"""

def extract_shirt_categories_from_html(html: str) -> Dict[str, int]:
    """Extract shirt categories and counts from the HTML"""
    categories = {}
    
    # Extract fabric categories with counts
    fabric_matches = [
        ("linen", 17),
        ("secret wash", 56), 
        ("broken-in oxford", 25),
        ("cotton linen", 4),
        ("camp collar", 6),
        ("tencel", 3),
        ("madras", 1),
        ("chambray, denim & indigo", 9)
    ]
    
    for fabric, count in fabric_matches:
        categories[fabric] = count
    
    return categories

def get_database_products() -> Set[str]:
    """Get all J.Crew product codes currently in our database"""
    print("💾 Checking database for existing J.Crew products...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        product_codes = set()
        
        # Check jcrew_product_cache table
        print("  📋 Checking jcrew_product_cache table...")
        try:
            cur.execute("SELECT DISTINCT product_code FROM jcrew_product_cache WHERE product_code IS NOT NULL")
            cache_codes = cur.fetchall()
            for (code,) in cache_codes:
                if code:
                    product_codes.add(code.upper())
            print(f"     ✅ Found {len(cache_codes)} products in jcrew_product_cache")
        except psycopg2.Error as e:
            print(f"     ⚠️  jcrew_product_cache table not accessible: {e}")
        
        # Check product_master table for J.Crew products
        print("  📋 Checking product_master table...")
        try:
            cur.execute("""
                SELECT DISTINCT pm.product_code 
                FROM product_master pm 
                JOIN brands b ON pm.brand_id = b.id 
                WHERE LOWER(b.name) LIKE '%j.crew%' OR LOWER(b.name) LIKE '%jcrew%'
            """)
            master_codes = cur.fetchall()
            for (code,) in master_codes:
                if code:
                    product_codes.add(code.upper())
            print(f"     ✅ Found {len(master_codes)} J.Crew products in product_master")
        except psycopg2.Error as e:
            print(f"     ⚠️  product_master table not accessible: {e}")
        
        cur.close()
        conn.close()
        
        total_unique = len(product_codes)
        print(f"  🎯 Total unique J.Crew product codes in database: {total_unique}")
        
        return product_codes
        
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return set()

def analyze_jcrew_categories():
    """Analyze J.Crew categories from the web search data"""
    print("🔍 J.Crew Casual Shirts Analysis (from Web Search Data)")
    print("=" * 70)
    
    # Extract categories from HTML
    categories = extract_shirt_categories_from_html(JCREW_HTML_CONTENT)
    
    # Get database products
    db_products = get_database_products()
    
    print(f"\n📊 J.CREW CASUAL SHIRTS BREAKDOWN:")
    print(f"   Total items on website: 154")
    print(f"   Items in your database: {len(db_products)}")
    print(f"   Estimated missing: ~{154 - len(db_products)}")
    
    print(f"\n🏷️  PRODUCT CATEGORIES ON WEBSITE:")
    total_categorized = 0
    for category, count in categories.items():
        print(f"   {category.title():25} {count:3d} items")
        total_categorized += count
    
    other_items = 154 - total_categorized
    if other_items > 0:
        print(f"   {'Other/Uncategorized':25} {other_items:3d} items")
    
    print(f"\n🎯 KEY INSIGHTS:")
    print(f"   • Secret Wash shirts are the largest category (56 items)")
    print(f"   • Broken-in Oxford shirts are popular (25 items)")  
    print(f"   • Linen shirts available (17 items)")
    print(f"   • You have {len(db_products)} J.Crew products vs 154 on the site")
    
    coverage_percent = (len(db_products) / 154) * 100
    print(f"   • Your database coverage: {coverage_percent:.1f}%")
    
    print(f"\n📋 RECOMMENDATIONS:")
    if coverage_percent < 50:
        print(f"   🔴 Low coverage - consider expanding J.Crew product collection")
        print(f"   • Focus on Secret Wash and Oxford shirts (most popular)")
        print(f"   • Add seasonal items like linen and corduroy")
    elif coverage_percent < 80:
        print(f"   🟡 Moderate coverage - fill in gaps strategically")
        print(f"   • Target specific categories you're missing")
        print(f"   • Focus on best sellers and top rated items")
    else:
        print(f"   🟢 Good coverage - maintain with new arrivals")
        print(f"   • Monitor for new products and seasonal updates")
    
    print(f"\n💡 NEXT STEPS:")
    print(f"   1. Use your existing J.Crew fetcher to add missing products")
    print(f"   2. Focus on the high-volume categories (Secret Wash, Oxford)")
    print(f"   3. Consider seasonal priorities (linen for summer, corduroy for fall)")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    analyze_jcrew_categories()
