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


def field(kind='k8s', *, background=True):
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
    canvas = '<rect width="600" height="640" fill="#080c1c"/>' if background else ''
    return canvas + '<ellipse cx="300" cy="320" rx="300" ry="340" fill="url(#glow)"/>' + constellation(600, 640) + orbital + core


def artwork(kind, title):
    return shell(600, 640, title, 'Original orbital line art with luminous blue and violet connections on a deep navy field.', field(kind))


def interactive_artwork():
    """Inline, inert first frame. Profile/image assets retain their exact bytes."""
    body = field('hero', background=False)
    stars = constellation(600, 640)
    body = body.replace(stars, '<g id="orbital-field">' + stars, 1)
    braid = helix(300, 92, 434, 62)
    body = body.replace(braid, '</g><g id="orbital-static-helix">' + braid + '</g>', 1)
    svg = shell(600, 640, 'Braided orbital field',
                'Original blue and violet orbital artwork with two interwoven strands.', body)
    # Namespace every inline ID to avoid collisions with HTML landmarks.
    for name in ('title', 'desc', 'strand', 'glow', 'panel'):
        svg = svg.replace(f'id="{name}"', f'id="orbital-{name}"').replace(f'#{name})', f'#orbital-{name})')
    return svg.replace('aria-labelledby="title desc"', 'aria-labelledby="orbital-title orbital-desc"')


def hero(data):
    name = escape(data['identity']['name'])
    lines = data['identity']['headline'].split('. ')
    headline = ''.join(f'<text x="48" y="{169+n*74}"' + (' fill="#c4b6ff"' if n == 2 else '') + f'>{escape(line.rstrip(".") + ".")}</text>' for n, line in enumerate(lines))
    return shell(1280, 480, data['identity']['headline'], 'Jenya: interfaces, networks and services. Original braided orbital illustration.', f'''
<rect width="1280" height="480" rx="16" fill="{BG}"/>
<g transform="translate(790 -37) scale(.87)">{field('hero')}</g>
<path d="M48 59 h34" stroke="#92b5ff" stroke-width="2"/>
<text x="96" y="66" font-family="Arial, sans-serif" font-size="22" fill="{MUTED}">{name} / justgithubaccount</text>
<g font-family="Arial, sans-serif" font-size="66" font-weight="600" fill="{WHITE}">
{headline}</g>
<text x="48" y="405" font-family="Arial, sans-serif" font-size="22" fill="{MUTED}">Interfaces · Networks · Services</text>''')


def compact_hero(data):
    lines = data['identity']['headline'].split('. ')
    headline = ''.join(f'<text x="32" y="{130+n*64}"' + (' fill="#c4b6ff"' if n == 2 else '') + f'>{escape(line.rstrip(".") + ".")}</text>' for n, line in enumerate(lines))
    return shell(640, 560, data['identity']['headline'], 'Interfaces, networks and services, with an original braided orbital illustration.', f'''
<rect width="640" height="560" rx="14" fill="{BG}"/>
<text x="32" y="54" font-family="Arial, sans-serif" font-size="21" fill="{MUTED}">{escape(data['identity']['name'])} / justgithubaccount</text>
<g transform="translate(345 262) scale(.45)">{field('hero')}</g>
<g font-family="Arial, sans-serif" font-size="54" font-weight="600" fill="{WHITE}">{headline}</g>
<g font-family="Arial, sans-serif" font-size="23" fill="{MUTED}"><text x="32" y="376">Interfaces</text><text x="32" y="414">Networks</text><text x="32" y="452">Services</text></g>''')


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

# The animated Profile hero is a projection of the reviewed public project
# categories. The original hero stays the static/reduced-motion fallback.
HERO_ORBIT_CSS = "#public-node-1,#public-node-2,#public-node-3{animation:orbit-projects 36s linear infinite}#public-node-2{animation-delay:-12s}#public-node-3{animation-delay:-24s}@keyframes orbit-projects{0.0000%{transform:translate(1180.00px,240.00px)}0.6944%{transform:translate(1179.85px,246.32px)}1.3889%{transform:translate(1179.39px,252.64px)}2.0833%{transform:translate(1178.63px,258.93px)}2.7778%{transform:translate(1177.57px,265.18px)}3.4722%{transform:translate(1176.21px,271.38px)}4.1667%{transform:translate(1174.55px,277.53px)}4.8611%{transform:translate(1172.59px,283.60px)}5.5556%{transform:translate(1170.35px,289.59px)}6.2500%{transform:translate(1167.82px,295.49px)}6.9444%{transform:translate(1165.01px,301.28px)}7.6389%{transform:translate(1161.92px,306.95px)}8.3333%{transform:translate(1158.56px,312.50px)}9.0278%{transform:translate(1154.94px,317.91px)}9.7222%{transform:translate(1151.06px,323.17px)}10.4167%{transform:translate(1146.94px,328.27px)}11.1111%{transform:translate(1142.57px,333.20px)}11.8056%{transform:translate(1137.96px,337.96px)}12.5000%{transform:translate(1133.14px,342.53px)}13.1944%{transform:translate(1128.09px,346.91px)}13.8889%{transform:translate(1122.85px,351.08px)}14.5833%{transform:translate(1117.40px,355.04px)}15.2778%{transform:translate(1111.77px,358.78px)}15.9722%{transform:translate(1105.97px,362.29px)}16.6667%{transform:translate(1100.00px,365.57px)}17.3611%{transform:translate(1093.88px,368.62px)}18.0556%{transform:translate(1087.62px,371.41px)}18.7500%{transform:translate(1081.23px,373.96px)}19.4444%{transform:translate(1074.72px,376.26px)}20.1389%{transform:translate(1068.11px,378.29px)}20.8333%{transform:translate(1061.41px,380.06px)}21.5278%{transform:translate(1054.63px,381.56px)}22.2222%{transform:translate(1047.78px,382.80px)}22.9167%{transform:translate(1040.88px,383.76px)}23.6111%{transform:translate(1033.94px,384.45px)}24.3056%{transform:translate(1026.98px,384.86px)}25.0000%{transform:translate(1020.00px,385.00px)}25.6944%{transform:translate(1013.02px,384.86px)}26.3889%{transform:translate(1006.06px,384.45px)}27.0833%{transform:translate(999.12px,383.76px)}27.7778%{transform:translate(992.22px,382.80px)}28.4722%{transform:translate(985.37px,381.56px)}29.1667%{transform:translate(978.59px,380.06px)}29.8611%{transform:translate(971.89px,378.29px)}30.5556%{transform:translate(965.28px,376.26px)}31.2500%{transform:translate(958.77px,373.96px)}31.9444%{transform:translate(952.38px,371.41px)}32.6389%{transform:translate(946.12px,368.62px)}33.3333%{transform:translate(940.00px,365.57px)}34.0278%{transform:translate(934.03px,362.29px)}34.7222%{transform:translate(928.23px,358.78px)}35.4167%{transform:translate(922.60px,355.04px)}36.1111%{transform:translate(917.15px,351.08px)}36.8056%{transform:translate(911.91px,346.91px)}37.5000%{transform:translate(906.86px,342.53px)}38.1944%{transform:translate(902.04px,337.96px)}38.8889%{transform:translate(897.43px,333.20px)}39.5833%{transform:translate(893.06px,328.27px)}40.2778%{transform:translate(888.94px,323.17px)}40.9722%{transform:translate(885.06px,317.91px)}41.6667%{transform:translate(881.44px,312.50px)}42.3611%{transform:translate(878.08px,306.95px)}43.0556%{transform:translate(874.99px,301.28px)}43.7500%{transform:translate(872.18px,295.49px)}44.4444%{transform:translate(869.65px,289.59px)}45.1389%{transform:translate(867.41px,283.60px)}45.8333%{transform:translate(865.45px,277.53px)}46.5278%{transform:translate(863.79px,271.38px)}47.2222%{transform:translate(862.43px,265.18px)}47.9167%{transform:translate(861.37px,258.93px)}48.6111%{transform:translate(860.61px,252.64px)}49.3056%{transform:translate(860.15px,246.32px)}50.0000%{transform:translate(860.00px,240.00px)}50.6944%{transform:translate(860.15px,233.68px)}51.3889%{transform:translate(860.61px,227.36px)}52.0833%{transform:translate(861.37px,221.07px)}52.7778%{transform:translate(862.43px,214.82px)}53.4722%{transform:translate(863.79px,208.62px)}54.1667%{transform:translate(865.45px,202.47px)}54.8611%{transform:translate(867.41px,196.40px)}55.5556%{transform:translate(869.65px,190.41px)}56.2500%{transform:translate(872.18px,184.51px)}56.9444%{transform:translate(874.99px,178.72px)}57.6389%{transform:translate(878.08px,173.05px)}58.3333%{transform:translate(881.44px,167.50px)}59.0278%{transform:translate(885.06px,162.09px)}59.7222%{transform:translate(888.94px,156.83px)}60.4167%{transform:translate(893.06px,151.73px)}61.1111%{transform:translate(897.43px,146.80px)}61.8056%{transform:translate(902.04px,142.04px)}62.5000%{transform:translate(906.86px,137.47px)}63.1944%{transform:translate(911.91px,133.09px)}63.8889%{transform:translate(917.15px,128.92px)}64.5833%{transform:translate(922.60px,124.96px)}65.2778%{transform:translate(928.23px,121.22px)}65.9722%{transform:translate(934.03px,117.71px)}66.6667%{transform:translate(940.00px,114.43px)}67.3611%{transform:translate(946.12px,111.38px)}68.0556%{transform:translate(952.38px,108.59px)}68.7500%{transform:translate(958.77px,106.04px)}69.4444%{transform:translate(965.28px,103.74px)}70.1389%{transform:translate(971.89px,101.71px)}70.8333%{transform:translate(978.59px,99.94px)}71.5278%{transform:translate(985.37px,98.44px)}72.2222%{transform:translate(992.22px,97.20px)}72.9167%{transform:translate(999.12px,96.24px)}73.6111%{transform:translate(1006.06px,95.55px)}74.3056%{transform:translate(1013.02px,95.14px)}75.0000%{transform:translate(1020.00px,95.00px)}75.6944%{transform:translate(1026.98px,95.14px)}76.3889%{transform:translate(1033.94px,95.55px)}77.0833%{transform:translate(1040.88px,96.24px)}77.7778%{transform:translate(1047.78px,97.20px)}78.4722%{transform:translate(1054.63px,98.44px)}79.1667%{transform:translate(1061.41px,99.94px)}79.8611%{transform:translate(1068.11px,101.71px)}80.5556%{transform:translate(1074.72px,103.74px)}81.2500%{transform:translate(1081.23px,106.04px)}81.9444%{transform:translate(1087.62px,108.59px)}82.6389%{transform:translate(1093.88px,111.38px)}83.3333%{transform:translate(1100.00px,114.43px)}84.0278%{transform:translate(1105.97px,117.71px)}84.7222%{transform:translate(1111.77px,121.22px)}85.4167%{transform:translate(1117.40px,124.96px)}86.1111%{transform:translate(1122.85px,128.92px)}86.8056%{transform:translate(1128.09px,133.09px)}87.5000%{transform:translate(1133.14px,137.47px)}88.1944%{transform:translate(1137.96px,142.04px)}88.8889%{transform:translate(1142.57px,146.80px)}89.5833%{transform:translate(1146.94px,151.73px)}90.2778%{transform:translate(1151.06px,156.83px)}90.9722%{transform:translate(1154.94px,162.09px)}91.6667%{transform:translate(1158.56px,167.50px)}92.3611%{transform:translate(1161.92px,173.05px)}93.0556%{transform:translate(1165.01px,178.72px)}93.7500%{transform:translate(1167.82px,184.51px)}94.4444%{transform:translate(1170.35px,190.41px)}95.1389%{transform:translate(1172.59px,196.40px)}95.8333%{transform:translate(1174.55px,202.47px)}96.5278%{transform:translate(1176.21px,208.62px)}97.2222%{transform:translate(1177.57px,214.82px)}97.9167%{transform:translate(1178.63px,221.07px)}98.6111%{transform:translate(1179.39px,227.36px)}99.3056%{transform:translate(1179.85px,233.68px)}100.0000%{transform:translate(1180.00px,240.00px)}}@media(prefers-reduced-motion:reduce){#public-node-1,#public-node-2,#public-node-3{animation:none!important}}"
HERO_ORBIT_START = (("1180.00", "240.00"), ("940.00", "365.57"), ("940.00", "114.43"))
HERO_ORBIT_COLORS = ("#79d8eb", "#b5a1fd", "#efc18e")


def animated_hero(data):
    original = hero(data)
    nodes = []
    for number, project in enumerate(data['projects'], 1):
        category = project['category'].split(' ', 1)
        first = escape(category[0].upper())
        second = escape(category[1].upper() if len(category) > 1 else '')
        x, y = HERO_ORBIT_START[number - 1]
        color = HERO_ORBIT_COLORS[number - 1]
        nodes.append(
            f'<g id="public-node-{number}" transform="translate({x} {y})">'
            f'<rect x="-78" y="-39" width="156" height="78" rx="15" fill="#151d39" stroke="{color}" stroke-width="1.6"/>'
            f'<circle cx="-62" cy="-23" r="3" fill="{color}"/>'
            f'<text x="-50" y="-18" font-family="Arial, sans-serif" font-size="11" fill="#cbd9fb">0{number}</text>'
            f'<text x="-68" y="10" font-family="Arial, sans-serif" font-size="16" font-weight="700" fill="#f1f2ff">{first}</text>'
            f'<text x="-68" y="28" font-family="Arial, sans-serif" font-size="12" fill="#bdc3df">{second}</text>'
            '</g>'
        )
    return original.replace('</svg>', '<style>' + HERO_ORBIT_CSS + '</style>' + ''.join(nodes) + '</svg>')
