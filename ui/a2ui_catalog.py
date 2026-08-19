"""
A2UI v0.8 BasicCatalog Component Definitions & Message Builders.
Strictly conforms to A2UI v0.8 Schema & BasicCatalog components:
- Column, Row, Card, Text, Button, Image, Icon, Divider, List
- Permitted BasicCatalog Icon names: "payment", "favorite", "check", "warning", "analytics"
- Pure ASCII data values for seamless ADK web preview & harness compatibility
"""

import json
from typing import Any, Dict, List, Optional, Union


def begin_rendering(surface_id: str, root_id: str) -> Dict[str, Any]:
    """Generates beginRendering directive."""
    return {
        "beginRendering": {
            "surfaceId": surface_id,
            "root": root_id
        }
    }


def surface_update(surface_id: str, components: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generates surfaceUpdate directive containing component definitions."""
    return {
        "surfaceUpdate": {
            "surfaceId": surface_id,
            "components": components
        }
    }


def data_model_update(surface_id: str, path: str = "/", contents: Optional[List[Any]] = None) -> Dict[str, Any]:
    """Generates dataModelUpdate directive."""
    return {
        "dataModelUpdate": {
            "surfaceId": surface_id,
            "path": path,
            "contents": contents if contents is not None else []
        }
    }


def make_text(
    comp_id: str,
    text: Optional[str] = None,
    path: Optional[str] = None,
    usage_hint: str = "body"
) -> Dict[str, Any]:
    """Builds a Text component with literalString or data binding path."""
    text_prop: Dict[str, Any] = {}
    if text is not None:
        text_prop["literalString"] = str(text)
    elif path is not None:
        text_prop["path"] = str(path)
    else:
        text_prop["literalString"] = ""

    comp: Dict[str, Any] = {
        "id": comp_id,
        "component": {
            "Text": {
                "text": text_prop,
                "usageHint": usage_hint
            }
        }
    }
    return comp


def make_column(
    comp_id: str,
    children_ids: List[str],
    alignment: str = "start"
) -> Dict[str, Any]:
    """Builds a Column layout component."""
    return {
        "id": comp_id,
        "component": {
            "Column": {
                "children": {
                    "explicitList": children_ids
                },
                "alignment": alignment
            }
        }
    }


def make_row(
    comp_id: str,
    children_ids: List[str],
    distribution: str = "start",
    alignment: str = "center"
) -> Dict[str, Any]:
    """Builds a Row layout component."""
    return {
        "id": comp_id,
        "component": {
            "Row": {
                "children": {
                    "explicitList": children_ids
                },
                "distribution": distribution,
                "alignment": alignment
            }
        }
    }


def make_card(
    comp_id: str,
    child_id: str,
    elevation: int = 1
) -> Dict[str, Any]:
    """Builds a Card container component."""
    return {
        "id": comp_id,
        "component": {
            "Card": {
                "child": child_id,
                "elevation": elevation
            }
        }
    }


def make_button(
    comp_id: str,
    child_id: str,
    action_name: str,
    action_context: Optional[Dict[str, Any]] = None,
    primary: bool = False
) -> Dict[str, Any]:
    """Builds a Button component with action handler and context."""
    ctx_list = []
    if action_context:
        for k, v in action_context.items():
            if isinstance(v, (int, float)):
                ctx_list.append({"key": k, "value": {"literalNumber": v}})
            elif isinstance(v, bool):
                ctx_list.append({"key": k, "value": {"literalBoolean": v}})
            else:
                ctx_list.append({"key": k, "value": {"literalString": str(v)}})

    return {
        "id": comp_id,
        "component": {
            "Button": {
                "child": child_id,
                "primary": primary,
                "action": {
                    "name": action_name,
                    "context": ctx_list
                }
            }
        }
    }


def make_image(
    comp_id: str,
    url: str,
    alt_text: str = "",
    fit: str = "contain",
    usage_hint: str = "largeFeature"
) -> Dict[str, Any]:
    """Builds an Image component."""
    return {
        "id": comp_id,
        "component": {
            "Image": {
                "url": {"literalString": url},
                "altText": {"literalString": alt_text},
                "fit": fit,
                "usageHint": usage_hint
            }
        }
    }


def make_icon(
    comp_id: str,
    icon_name: str = "analytics"
) -> Dict[str, Any]:
    """Builds an Icon component. Permitted: 'payment', 'favorite', 'check', 'warning', 'analytics'."""
    allowed = ["payment", "favorite", "check", "warning", "analytics"]
    valid_icon = icon_name if icon_name in allowed else "analytics"
    return {
        "id": comp_id,
        "component": {
            "Icon": {
                "icon": {"literalString": valid_icon}
            }
        }
    }


def make_divider(comp_id: str) -> Dict[str, Any]:
    """Builds a visual Divider component."""
    return {
        "id": comp_id,
        "component": {
            "Divider": {}
        }
    }


def make_list_template(
    comp_id: str,
    item_template_id: str,
    data_binding_path: str = "/items"
) -> Dict[str, Any]:
    """Builds a data-bound List component."""
    return {
        "id": comp_id,
        "component": {
            "List": {
                "children": {
                    "template": {
                        "componentId": item_template_id,
                        "dataBinding": data_binding_path
                    }
                }
            }
        }
    }


def format_a2ui_payload(messages: List[Dict[str, Any]]) -> str:
    """Formats an array of A2UI messages wrapped in <a2ui-json> tags."""
    json_str = json.dumps(messages, indent=2, ensure_ascii=True)
    return f"<a2ui-json>\n{json_str}\n</a2ui-json>"
