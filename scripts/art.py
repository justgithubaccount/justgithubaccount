"""Original static vector constructions. No tracing, raster data or remote resources."""
from html import escape
import math

BG = '#080c1c'
WHITE = '#f1f2ff'
MUTED = '#bdc3df'


def shell(width, height, title, description, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>
<defs>
<linearGradient id="strand" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#69dbff"/><stop offset=".5" stop-color="#777bff"/><stop offset="1" stop-color="#d1a1ff"/></linearGradient>
<radialGradient id="glow"><stop stop-color="#6555cc" stop-opacity=".28"/><stop offset="1" stop-color="#080c1c" stop-opacity="0"/></radialGradient>
<linearGradient id="panel" x2="1" y2="1"><stop stop-color="#182541"/><stop offset="1" stop-color="#11142c"/></linearGradient>
</defs>
{body}
</svg>
'''


def path(points):
    return 'M' + ' L'.join(f'{x:.2f},{y:.2f}' for x, y in points)


def helix(cx=300, top=105, height=450, amplitude=65):
    # A new parametric braid: two waves joined by ribs, inside an orbital field.
    parts = []
    for i in range(33):
        y = top + i * height / 32
        x = amplitude * math.sin(i * math.pi / 8)
        parts.append(f'<path d="M{cx-x:.2f},{y:.2f} L{cx+x:.2f},{y:.2f}" stroke="#aba4ff" stroke-width="1" opacity=".38"/>')
    for sign in (-1, 1):
        pts = [(cx + sign * amplitude * math.sin(i * math.pi / 32), top + i * height / 128) for i in range(129)]
        parts.append(f'<path d="{path(pts)}" stroke="url(#strand)" stroke-width="3" fill="none"/>')
    return ''.join(parts)


def constellation(width, height):
    # Fixed arithmetic instead of random state: bytes are stable across builds.
    return ''.join(f'<circle cx="{(i*137+29)%width}" cy="{(i*89+41)%height}" r="{1 if i%4 else 1.7}" fill="#9fafff" opacity="{.15+(i%5)*.1:.2f}"/>' for i in range(48))


def field(kind='k8s'):
    orbital = '''<circle cx="300" cy="310" r="224" fill="none" stroke="#525caa" opacity=".25"/>
<circle cx="300" cy="310" r="190" fill="none" stroke="#454b8b" opacity=".28" stroke-dasharray="2 12"/>
<ellipse cx="300" cy="310" rx="265" ry="95" transform="rotate(-32 300 310)" fill="none" stroke="#7f78dc" opacity=".32"/>
<ellipse cx="300" cy="310" rx="259" ry="102" transform="rotate(38 300 310)" fill="none" stroke="#65c6ea" opacity=".22"/>
'''
    if kind == 'hero':
        core = helix(300, 92, 434, 62)
        core += '<ellipse cx="300" cy="550" rx="95" ry="19" fill="none" stroke="#b39cff" opacity=".55"/>'
        core += '<ellipse cx="300" cy="550" rx="132" ry="28" fill="none" stroke="#6464b2" opacity=".3"/>'
        for sign in (-1, 1):
            core += f'<path d="M300 526 C{300+sign*125} 485 {300+sign*60} 425 {300+sign*147} 399" fill="none" stroke="url(#strand)" opacity=".6"/>'
    else:
        # Open, connected panels reinterpret the graph reference without vendor marks.
        centers = {'k8s': [(155, 210), (390, 185), (300, 405)], 'infra': [(150, 225), (340, 310), (430, 430)], 'fastapi': [(165, 210), (360, 230), (270, 420)]}[kind]
        core = ''
        for a, b in zip(centers, centers[1:] + centers[:1]):
            core += f'<path d="M{a[0]} {a[1]} L{b[0]} {b[1]}" stroke="url(#strand)" stroke-width="1.5" opacity=".65"/>'
        for i, (x, y) in enumerate(centers):
            core += f'<rect x="{x-58}" y="{y-40}" width="116" height="80" rx="10" fill="url(#panel)" stroke="url(#strand)"/>'
            if kind == 'fastapi':
                core += f'<path d="M{x-30} {y-9} h60 M{x-30} {y+5} h43 M{x-30} {y+19} h24" stroke="#b5b6ef" stroke-width="2"/>'
            elif kind == 'infra':
                core += f'<path d="M{x-28} {y+10} l28 -25 28 25 -28 16 z M{x-28} {y-2} l28 17 28 -17" fill="none" stroke="#b5b6ef" stroke-width="2"/>'
            else:
                core += f'<circle cx="{x}" cy="{y}" r="20" fill="none" stroke="#b5b6ef"/><path d="M{x-9} {y} h18 M{x} {y-9} v18" stroke="#b5b6ef"/>'
            core += f'<circle cx="{x}" cy="{y+40}" r="3" fill="#8bdcff"/>'
    return '<rect width="600" height="640" fill="#080c1c"/><ellipse cx="300" cy="320" rx="300" ry="340" fill="url(#glow)"/>' + constellation(600, 640) + orbital + core


def artwork(kind, title):
    return shell(600, 640, title, 'Original orbital line art with luminous blue and violet connections on a deep navy field.', field(kind))


def hero(data):
    name = escape(data['identity']['name'])
    lines = data['identity']['headline'].split('. ')
    headline = ''.join(f'<text x="48" y="{169+n*74}"' + (' fill="#c4b6ff"' if n == 2 else '') + f'>{escape(line.rstrip(".") + ".")}</text>' for n, line in enumerate(lines))
    return shell(1280, 480, data['identity']['headline'], 'Jenya: Python applications, cloud infrastructure and GitOps. Original braided orbital illustration.', f'''
<rect width="1280" height="480" rx="16" fill="{BG}"/>
<g transform="translate(790 -37) scale(.87)">{field('hero')}</g>
<path d="M48 59 h34" stroke="#92b5ff" stroke-width="2"/>
<text x="96" y="66" font-family="Arial, sans-serif" font-size="22" fill="{MUTED}">{name} / justgithubaccount</text>
<g font-family="Arial, sans-serif" font-size="66" font-weight="600" fill="{WHITE}">
{headline}</g>
<text x="48" y="405" font-family="Arial, sans-serif" font-size="22" fill="{MUTED}">Python APIs · Cloud infrastructure · GitOps</text>''')


def compact_hero(data):
    lines = data['identity']['headline'].split('. ')
    headline = ''.join(f'<text x="32" y="{130+n*64}"' + (' fill="#c4b6ff"' if n == 2 else '') + f'>{escape(line.rstrip(".") + ".")}</text>' for n, line in enumerate(lines))
    return shell(640, 560, data['identity']['headline'], 'Python APIs, cloud infrastructure and GitOps, with a new braided orbital illustration.', f'''
<rect width="640" height="560" rx="14" fill="{BG}"/>
<text x="32" y="54" font-family="Arial, sans-serif" font-size="21" fill="{MUTED}">{escape(data['identity']['name'])} / justgithubaccount</text>
<g transform="translate(345 262) scale(.45)">{field('hero')}</g>
<g font-family="Arial, sans-serif" font-size="54" font-weight="600" fill="{WHITE}">{headline}</g>
<g font-family="Arial, sans-serif" font-size="23" fill="{MUTED}"><text x="32" y="376">Python APIs</text><text x="32" y="414">Cloud infrastructure</text><text x="32" y="452">GitOps</text></g>''')


def compact_card(project, index):
    return shell(640, 320, project['title'], project['category'] + '. Public source code; engineering lab.', f'''
<rect x="1" y="1" width="638" height="318" rx="12" fill="{BG}" stroke="#363a5a"/>
<g transform="translate(460 130) scale(.28)">{field(project['id'])}</g>
<text x="28" y="53" fill="#a9c8ff" font-family="Arial, sans-serif" font-size="22">0{index} / {escape(project['category'])}</text>
<text x="28" y="118" fill="{WHITE}" font-family="Arial, sans-serif" font-size="35" font-weight="600">{escape(project['title'])}</text>
<text x="28" y="174" fill="{MUTED}" font-family="Arial, sans-serif" font-size="21">{escape(' · '.join(project['tags']))}</text>
<path d="M28 261 h26 m-7 -7 7 7 -7 7" fill="none" stroke="#c4b6ff" stroke-width="2"/>
<text x="70" y="268" fill="#c4b6ff" font-family="Arial, sans-serif" font-size="21">Explore the repository</text>''')


def card(project, index):
    return shell(1040, 280, project['title'], project['category'] + '. Public source code; engineering lab.', f'''
<rect x="1" y="1" width="1038" height="278" rx="12" fill="{BG}" stroke="#363a5a"/>
<g transform="translate(752 -16) scale(.48)">{field(project['id'])}</g>
<text x="38" y="57" fill="#a9c8ff" font-family="Arial, sans-serif" font-size="19">0{index} / {escape(project['category'])}</text>
<text x="38" y="124" fill="{WHITE}" font-family="Arial, sans-serif" font-size="40" font-weight="600">{escape(project['title'])}</text>
<text x="38" y="176" fill="{MUTED}" font-family="Arial, sans-serif" font-size="21">{escape(' · '.join(project['tags']))}</text>
<path d="M38 220 h26 m-7 -7 7 7 -7 7" fill="none" stroke="#c4b6ff" stroke-width="2"/>
<text x="80" y="227" fill="#c4b6ff" font-family="Arial, sans-serif" font-size="19">Explore the public repository</text>''')
