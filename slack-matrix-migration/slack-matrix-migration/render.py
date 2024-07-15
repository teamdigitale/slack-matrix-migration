from emoji import emojize
from slack_sdk.models.blocks import Block, RichTextElement, RichTextBlock, RichTextElementParts, RichTextSectionElement, RichTextListElement, RichTextPreformattedElement, RichTextQuoteElement

def render(block: RichTextBlock, luts)-> str:
    ret = ""
    for e in block.elements:
        match e.type:
            case "rich_text_section":
                ret += renderRichTextSection(e, luts)
            case "rich_text_list":
                ret += renderRichTextList(e, luts)
            case "rich_text_preformatted":
                ret += renderRichTextPreformatted(e, luts)
            case "rich_text_quote":
                ret += renderRichTextQuote(e, luts)
    return ret

def renderText(e: RichTextElementParts.Text) -> str:
    ret = e.text
    if e.style != None:
        ret = addStyle(ret, e.style)
    return ret

def addStyle(text: str, style) -> str:
    is_bold = ("bold" in style) and style["bold"]
    is_italic = ("italic" in style) and style["italic"]
    is_strike = ("strike" in style) and style["strike"]
    is_code = ("code" in style) and style["code"]
 
    ret = text
    if (is_strike): ret = f"<s>{ret}</s>"
    if (is_italic): ret = f"<i>{ret}</i>"
    if (is_bold): ret = f"<b>{ret}</b>"
    if (is_code): ret = f"<code>{ret}</code>"

    return ret

def renderLink(e: RichTextElementParts.Link) -> str:
    text = e.text if e.text != None else e.url
    ret = f"<a href=\"{e.url}\">{text}</a>"
    if e.style != None:
        ret = addStyle(ret, e.style)
    return ret

def renderEmoji(e: RichTextElementParts.Emoji) -> str:
    return emojize(f":{e.name}:", language='alias')

def renderUser(e: RichTextElementParts.User, luts) -> str:
    if not e.user_id in luts["userLUT"]:
        return f"<@{e.user_id}>"
    user_id = luts["userLUT"][e.user_id]
    display_name = luts["nameLUT"][user_id]
    ret = f"<a href=\"https://matrix.to/#/{user_id}\">{display_name}</a>"
    if e.style != None:
        ret = addStyle(ret, e.style)
    return ret

def renderChannel(e: RichTextElementParts.Channel, luts) -> str:
    if not e.channel_id in luts["roomLUT"]:
        return f"<#{e.channel_id}>"
    channel_id = luts["roomLUT"][e.channel_id]
    domain = channel_id.split(":", 1)[1]
    display_name = f"#{luts['roomLUT2'][e.channel_id]}:{domain}"
    ret = f"<a href=\"https://matrix.to/#/{display_name}\">{display_name}</a>"
    if e.style != None:
        ret = addStyle(ret, e.style)
    return ret

def renderRichTextSection(e: RichTextSectionElement, luts) -> str:
    ret = "<p>"

    for elem in e.elements:
        ret += renderRichTextElement(elem, luts)
    ret += "</p>"
    return ret

def renderRichTextElement(e: RichTextElement, luts) -> str:
    ret = ""

    match e.type:
        case "channel":
            ret += renderChannel(e, luts)
        case "emoji":
            ret += renderEmoji(e)
        case "link":
            ret += renderLink(e)
        case "text":
            ret += renderText(e)
        case "user":
            ret += renderUser(e, luts)
#        case "usergroup":
#            ret += renderUserGroup(e)
    
    return ret

def renderRichTextList(e: RichTextListElement, luts) -> str:
    ret = "<ul>" if e.style == "bullet" else "<ol>"

    for l in e.elements:
        ret += f"<li>{renderRichTextSection(l, luts)}</li>"

    ret += "</ul>" if e.style == "bullet" else "</ol>"

    return ret

def renderRichTextPreformatted(e: RichTextPreformattedElement, luts) -> str:
    ret = "<pre>"
    for l in e.elements:
        ret += renderRichTextElement(l, luts)
    ret += "</pre>"
    return ret

def renderRichTextQuote(e: RichTextQuoteElement, luts) -> str:
    ret = "<blockquote>"
    for l in e.elements:
        ret += renderRichTextElement(l, luts)
    ret += "</blockquote>"
    return ret
