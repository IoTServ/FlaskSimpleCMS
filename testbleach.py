# coding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import bleach
tags = ['font', 'span', 'div', 'table', 'td', 'th', 'a', 'img', 'p', 'ol' ,'ul', 'li',
 'blockquote', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'pre', 'hr', 'br','tbody','tr','strong',
 'b','sub','sup','em','i','u','strike','s','del']
attrs = {
        '*': ['style','align','class'],
        'font' : ['color', 'size', 'face'],
        'table': ['border', 'cellspacing', 'cellpadding', 'width', 'height', 'bordercolor'],
        'td': ['valign', 'width', 'height', 'colspan', 'rowspan', 'bgcolor'],
        'th': ['valign', 'width', 'height', 'colspan', 'rowspan', 'bgcolor'],
        'a' : ['href', 'target', 'name'],
        'img' : ['src', 'width', 'height', 'border', 'alt', 'title']
}
styles = ['background-color', 'color', 'font-size', 'font-family', 'background',
                'font-weight', 'font-style', 'text-decoration', 'vertical-align',
                'line-height','border', 'margin', 'padding', 'text-align',
                'margin-left', 'bgcolor', 'width', 'height', 'border-collapse',
                'text-indent', 'page-break-after']

if __name__ == '__main__':
    print bleach.clean(
    u'<INPUT SRC=”javascript:alert(‘XSS’);”>',
    tags = tags,
    attributes = attrs,
    styles = styles)