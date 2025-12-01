#!/usr/bin/env python3
"""
Lululemon PDP GraphQL client.

Usage examples
--------------

Pull a PDP using variables derived from a saved __NEXT_DATA__ blob:

    python scripts/lululemon_graphql_client.py \
        --payload data/tmp/lululemon_prod11500060.json \
        --output data/tmp/lululemon_prod11500060.graphql.json

Override any variable explicitly:

    python scripts/lululemon_graphql_client.py \
        --product-id prod11500060 \
        --category ABC-Slim-Trouser-32 \
        --unified-id n1blegzu9dn \
        --locale en-US

The script warms up https://shop.lululemon.com/ to satisfy Akamai cookies
before issuing a POST to /api/graphql.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

REQUESTS_IMPORT_ERROR = None
try:  # pragma: no cover - only triggered in sandboxed envs
    import requests
except Exception as exc:  # noqa: BLE001
    REQUESTS_IMPORT_ERROR = exc
    requests = None  # type: ignore

__all__ = [
    "REQUESTS_IMPORT_ERROR",
    "execute_query",
    "response_to_ingest_payload",
]

GRAPHQL_URL = "https://shop.lululemon.com/api/graphql"
HOMEPAGE_URL = "https://shop.lululemon.com/"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://shop.lululemon.com",
    "Referer": "https://shop.lululemon.com/",
}

GET_PDP_DATA_BY_ID = """query GetPdpDataById(
  $id: String!
  $category: String! = ""
  $unifiedId: String! = ""
  $locale: String
  $fetchPcmMedia: Boolean!
  $fetchVariants: Boolean!
) {
  productDetailPage(
    id: $id
    category: $category
    unifiedId: $unifiedId
    locale: $locale
  ) {
    allInseam {
      productId
      productUrl
      inseam
    }
    allLocalePids {
      CA
      US
      siteId
      pdpUrl
      categoryUnifiedId
      productUnifiedId
    }
    allSize {
      size
      available
    }
    category {
      id
      name
    }
    colorDriver {
      color
      sizes
    }
    colorAttributes {
      colorId
      styleColorId
      wwmt
      fabricPill
      colorGroups
      designedFor {
        activityText
        iconId
      }
      careAndContent {
        iconId
        title
        sections {
          media
          title
          attributes {
            badgeId
            badgeText
            iconId
            list {
              items
              title
            }
            text
          }
        }
      }
      fabricOrBenefits {
        iconId
        title
        sections {
          media {
            captionText
            imageAlt
            videoSrcPortrait
            videoPosterSrc
            videoPosterSrcPortrait
            imageSrc
            videoSrc
          }
          title
          attributes {
            iconId
            list
            text
            attributeType
          }
        }
      }
      fitOrHowToUse {
        id
        iconId
        title
        sections {
          media {
            captionText
            imageAlt
            videoSrcPortrait
            videoPosterSrc
            videoPosterSrcPortrait
            imageSrc
            videoSrc
          }
          title
          attributes {
            iconId
            list
            text
            attributeType
          }
        }
      }
      featuresOrIngredients {
        id
        iconId
        title
        sections {
          media {
            captionText
            imageAlt
            videoSrcPortrait
            videoPosterSrc
            videoPosterSrcPortrait
            imageSrc
            videoSrc
          }
          title
          attributes {
            iconId
            list
            text
            attributeType
          }
        }
      }
    }
    colors {
      code
      name
      swatchUrl
      slug
      simpleRanking
      ituBt709
      ituBt601
      colorHarmonyRank
    }
    highlights {
      highlightIconWeb
      highlightLabel
      visibility
      subText
      abFlag {
        name
        abFlagName
        showIcon
        showSubText
        showHighlight
        visibility
      }
    }
    pcmProductStyleInfo @include(if: $fetchPcmMedia) {
      departmentId
      divisionId
    }
    pcmProductVideoInfo {
      type
      url
      posterImageUrl
    }
    productAttributes {
      productContentCare {
        colorId
        heroBannerHotSpotText
        care {
          careId
          careDescription
          iconImgUrl
        }
      }
      productContentFeature {
        f5ContentAlignmentPDP
        styleId
        f5Features {
          featureName
          featureDescription
        }
      }
      productContentFabric {
        fabricDescription
        fabricDisplayName
        fabricId
        fabricPurposes
      }
      productContentWhyWeMadeThis
    }
    productCarousel {
      color {
        code
        name
        swatchUrl
        slug
        simpleRanking
        ituBt709
        ituBt601
        colorHarmonyRank
      }
      modelInfo {
        description
        modelIsWearing {
          productName
          numberOfAvailableColors
          url
          imageURL
          onSale
          listPrice
          salePrice
        }
        shopThisLook
      }
      imageInfo
      inseam
      mediaInfo {
        type
        url
        posterImageUrl
      }
      pcmMediaInfo @include(if: $fetchPcmMedia) {
        type
        url
        posterImageUrl
      }
    }
    productSummary {
      productId
      displayName
      unifiedId
      parentCategoryUnifiedId
      pdpUrl
      pdpUrlWithRegion
      productUrl
      shareUrl
      whyWeMadeThis
      isFinalSale
      isSoldOut
      isLoyaltyProduct
      isHazmatProduct
      divisionId
      featuredFabric
      fitDetails
      departmentId
      activity
      allAncestorsDisplayName
      allAncestorsRepositoryId
      allAvailableSizes
      bazaarVoiceID
      collections
      colorGroup
      colour
      commonId
      currencyCode
      defaultParentCategory
      defaultSku
      display
      displayCA
      displayNameWithBr
      f5BckimgUrl
      freeReturnShipping
      gender
      genderCategoryTitle
      genderCategoryProductTitle
      hasLinkedProducts
      imageScheme
      isDisplayable
      isProductLocaleMatch
      itemType
      linkedProducts
      listPrice
      locale
      loyaltyTermsAndConditions {
        url
        text
      }
      onSale
      parentCategoryDisplayName
      parentCategoryKeywords
      price
      priceRange
      productActivityIdRepositoryId
      productApplicableSystems
      productBaseUrl
      productCatalogId
      productCategory
      productDefaultSort
      productDisallowAsRecommendation
      productHasOutfitProduct
      productLanguage
      productLastSkuAdditionDateTime
      productMarkDown
      productName
      productNoFollow
      productNoIndex
      productNumberOfImageAssets
      productOnSale
      productSiteMapPdpUrl
      productSizes
      productWhatsNew
      skuSkuImages
      skuStyleOrder
      title
      trendingColorsAll
      topSellers
      type
      newColors
    }
    productVariants {
      attributeType
      colorCode
      description
      fabric
      fit
      imageUrl
      label
      name
      path
      productId
      type
      value
    }
    refinementCrumbs {
      displayName
      dimensionName
      label
      multiSelect
      properties {
        navigationState
        nValue
      }
      ancestors {
        label
        navigationState
        properties {
          navigationState
          nValue
        }
      }
    }
    sizeDriver {
      size
      colors
    }
    sizeGuide {
      url
      category
    }
    skus {
      id
      skuUrl
      price {
        listPrice
        currency {
          code
          symbol
        }
        onSale
        salePrice
        earlyAccessMarkdownPrice
      }
      size
      color {
        code
        name
        swatchUrl
        slug
        simpleRanking
        ituBt709
        ituBt601
        colorHarmonyRank
      }
      available
      inseam
      styleId
      styleNumber
    }
    tier
    variants @include(if: $fetchVariants) {
      color {
        code
        name
        swatchUrl
        slug
        simpleRanking
        ituBt709
        ituBt601
        colorHarmonyRank
      }
      skus {
        id
        skuUrl
        price {
          listPrice
          currency {
            code
            symbol
          }
          onSale
          salePrice
          earlyAccessMarkdownPrice
        }
        size
        color {
          code
          name
          swatchUrl
          slug
          simpleRanking
          ituBt709
          ituBt601
          colorHarmonyRank
        }
        available
        inseam
        styleId
        styleNumber
      }
      imageSet {
        images {
          url
          alt
        }
        modelDescription
      }
    }
    whyWeMadeThisAttributes {
      text
      image
    }
  }
}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Call Lululemon's PDP GraphQL endpoint."
    )
    parser.add_argument(
        "--payload",
        type=Path,
        help="Optional __NEXT_DATA__ JSON file to derive variables.",
    )
    parser.add_argument("--product-id")
    parser.add_argument("--category")
    parser.add_argument("--unified-id")
    parser.add_argument("--locale")
    parser.add_argument(
        "--fetch-pcm-media",
        action="store_true",
        default=True,
        help="Include PCM media blocks (default: true).",
    )
    parser.add_argument(
        "--no-fetch-pcm-media",
        dest="fetch_pcm_media",
        action="store_false",
        help="Disable PCM media blocks.",
    )
    parser.add_argument(
        "--fetch-variants",
        action="store_true",
        default=True,
        help="Include variants block (default: true).",
    )
    parser.add_argument(
        "--no-fetch-variants",
        dest="fetch_variants",
        action="store_false",
        help="Disable variants block.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to save the GraphQL JSON response.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON response to stdout.",
    )
    return parser.parse_args()


def derive_variables_from_payload(payload_path: Path) -> Dict[str, Any]:
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    page_props = payload.get("props", {}).get("pageProps", {})

    path = page_props.get("path") or ""
    path_parts = path.split("/")
    category_slug = path_parts[3] if len(path_parts) > 3 else ""

    dehydrated_queries = (
        page_props.get("dehydratedState", {}).get("queries", [])
    )
    pdp_data: Optional[dict] = None
    for query in dehydrated_queries:
        key = query.get("queryKey") or []
        if key and key[0] == "pdp":
            pdp_data = query.get("state", {}).get("data")
            break

    if not pdp_data:
        raise RuntimeError(
            "Unable to locate PDP data inside dehydratedState. "
            "Was the payload captured from a PDP page?"
        )

    summary = pdp_data.get("productSummary") or {}

    return {
        "id": page_props.get("productId") or summary.get("productId"),
        "category": category_slug,
        "unifiedId": summary.get("unifiedId")
        or pdp_data.get("allLocalePids", {}).get("categoryUnifiedId", ""),
        "locale": (
            summary.get("locale")
            or page_props.get("locale")
            or page_props.get("akamaiDevice", {}).get("locale")
        ),
    }


def merge_variables(
    args: argparse.Namespace, payload_vars: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    def pick(key: str) -> Any:
        if getattr(args, key.replace("-", "_"), None):
            return getattr(args, key.replace("-", "_"))
        if payload_vars and payload_vars.get(key):
            return payload_vars[key]
        raise RuntimeError(
            f"Missing required GraphQL variable '{key}'. "
            "Pass it explicitly or provide a payload with that field."
        )

    return {
        "id": pick("id"),
        "category": pick("category"),
        "unifiedId": pick("unifiedId"),
        "locale": pick("locale"),
        "fetchPcmMedia": args.fetch_pcm_media,
        "fetchVariants": args.fetch_variants,
    }


def warm_up_session(session: requests.Session) -> None:
    response = session.get(HOMEPAGE_URL, timeout=30)
    response.raise_for_status()


def _require_requests() -> None:
    if not requests:
        raise RuntimeError(
            "The 'requests' package is unavailable. "
            f"Original import error: {REQUESTS_IMPORT_ERROR}"
        )


def execute_query(variables: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute the GetPdpDataById GraphQL query with the provided variables.
    """
    _require_requests()
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    warm_up_session(session)
    gql_payload = {
        "operationName": "GetPdpDataById",
        "variables": variables,
        "query": GET_PDP_DATA_BY_ID,
    }
    response = session.post(
        GRAPHQL_URL, json=gql_payload, timeout=45, headers=DEFAULT_HEADERS
    )
    response.raise_for_status()
    return response.json()


def main() -> None:
    args = parse_args()
    payload_vars: Optional[Dict[str, Any]] = None
    if args.payload:
        payload_vars = derive_variables_from_payload(args.payload)

    variables = merge_variables(args, payload_vars)
    result = execute_query(variables)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")

    if args.pretty or not args.output:
        json.dump(result, sys.stdout, indent=2 if args.pretty else None)
        sys.stdout.write("\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover
        print(f"❌ {exc}", file=sys.stderr)
        sys.exit(1)


def response_to_ingest_payload(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrap a GraphQL response so the existing ingest pipeline (which expects
    productDetailPage.current within initialStoreState) can consume it.
    """
    product_detail = response.get("data", {}).get("productDetailPage")
    if not product_detail:
        raise RuntimeError("GraphQL response missing data.productDetailPage")

    return {
        "props": {
            "pageProps": {
                "initialStoreState": {
                    "productDetailPage": {
                        "current": product_detail,
                    }
                }
            }
        }
    }

