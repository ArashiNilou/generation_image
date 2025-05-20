import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import base64
from io import BytesIO
from PIL import Image
import os

def extract_logo(url):
    """
    Extrait le logo principal d'un site web en utilisant plusieurs méthodes
    Retourne un dictionnaire avec les informations du logo ou None si aucun logo n'est trouvé
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extraire le domaine pour des comparaisons plus tard
        domain_parts = urllib.parse.urlparse(url).netloc.split('.')
        domain = domain_parts[-2] if len(domain_parts) >= 2 else domain_parts[0]
        
        # Méthode 1: Priorité aux logos explicitement marqués
        logo_candidates = []
        
        # 1.1 Rechercher les éléments portant explicitement 'logo' dans les attributs
        for element in soup.select('[class*="logo"], [id*="logo"]'):
            # Chercher une image à l'intérieur
            logo_img = element.find('img')
            if logo_img and logo_img.get('src'):
                logo_candidates.append({
                    'img': logo_img,
                    'score': 100,  # Score très élevé pour les logos explicites
                    'source': 'explicit_logo_class'
                })
            # Si pas d'image, regarder si c'est un lien avec une image
            elif element.name == 'a' and element.find('img'):
                logo_img = element.find('img')
                if logo_img and logo_img.get('src'):
                    logo_candidates.append({
                        'img': logo_img,
                        'score': 90,
                        'source': 'logo_link_img'
                    })
        
        # 1.2 Rechercher les images avec logo dans les attributs ou le chemin
        logo_patterns = [r'logo', r'brand', r'header-image', r'site-logo', r'main-logo']
        for img in soup.find_all('img'):
            img_src = img.get('src', '')
            img_alt = img.get('alt', '')
            img_class = ' '.join(img.get('class', []))
            img_id = img.get('id', '')
            
            # Calculer un score initial pour cette image
            score = 0
            source = ''
            
            # Vérifier si l'image porte explicitement le mot "logo"
            for pattern in logo_patterns:
                if re.search(pattern, img_src, re.IGNORECASE):
                    score += 50
                    source = 'src_contains_logo'
                    break
                elif re.search(pattern, img_alt, re.IGNORECASE):
                    score += 40
                    source = 'alt_contains_logo'
                    break
                elif re.search(pattern, img_class, re.IGNORECASE):
                    score += 45
                    source = 'class_contains_logo'
                    break
                elif re.search(pattern, img_id, re.IGNORECASE):
                    score += 45
                    source = 'id_contains_logo'
                    break
            
            # Si un score a été attribué, ajouter aux candidats
            if score > 0:
                logo_candidates.append({
                    'img': img,
                    'score': score,
                    'source': source
                })
        
        # Méthode 2: Emplacement stratégique - les logos sont généralement en haut de page
        # 2.1 Logo dans l'en-tête
        header_elements = soup.select('header, .header, #header')
        for header in header_elements:
            # Chercher d'abord les éléments avec "logo" dans la classe/id dans l'en-tête
            logo_elements = header.select('[class*="logo"], [id*="logo"]')
            for logo_element in logo_elements:
                logo_img = logo_element.find('img')
                if logo_img and logo_img.get('src'):
                    logo_candidates.append({
                        'img': logo_img,
                        'score': 85,
                        'source': 'header_logo_element'
                    })
            
            # Sinon chercher toutes les images dans l'en-tête, mais avec un score plus faible
            if not logo_elements:
                for img in header.find_all('img', limit=3):  # Limiter aux 3 premières images
                    if img.get('src'):
                        # Vérifier si c'est probablement un logo
                        score = 35
                        is_small_icon = False
                        
                        # Éviter les petites icônes
                        if img.get('width') and img.get('height'):
                            try:
                                width = int(img['width'])
                                height = int(img['height'])
                                if width < 20 or height < 20:
                                    is_small_icon = True
                                    score -= 20
                            except ValueError:
                                pass
                        
                        if not is_small_icon:
                            logo_candidates.append({
                                'img': img,
                                'score': score,
                                'source': 'header_img'
                            })
        
        # 2.2 Logo dans la barre de navigation
        navbar_elements = soup.select('nav, .navbar, .nav, #navbar, #nav')
        for navbar in navbar_elements:
            for img in navbar.find_all('img', limit=2):  # Limiter pour éviter les icônes de navigation
                if img.get('src'):
                    score = 30
                    # Bonus si l'image est dans un lien vers la page d'accueil
                    parent_a = img.find_parent('a')
                    if parent_a and parent_a.get('href'):
                        href = parent_a.get('href')
                        if href == '/' or href == '#' or href == url or href.endswith('index.html'):
                            score += 20
                    
                    logo_candidates.append({
                        'img': img,
                        'score': score,
                        'source': 'navbar_img'
                    })
        
        # 2.3 Première image visible en haut de page (souvent le logo)
        top_images = soup.select('body > img, body > div > img, body > header > img, body > div > header > img')
        if top_images:
            logo_candidates.append({
                'img': top_images[0],
                'score': 25,
                'source': 'top_image'
            })
            
        # Méthode 3: Contenu de l'image
        for candidate in list(logo_candidates):  # Copie de la liste pour pouvoir modifier
            img = candidate['img']
            img_alt = img.get('alt', '').lower()
            img_src = img.get('src', '').lower()
            
            # Bonus si l'image contient le nom du domaine
            if domain.lower() in img_alt or domain.lower() in img_src:
                candidate['score'] += 15
                candidate['source'] += '_with_domain'
            
            # Pénalité pour les images qui sont probablement des bannières ou des produits
            if 'banner' in img_src or 'banner' in img_alt:
                candidate['score'] -= 30
            if 'product' in img_src or 'product' in img_alt:
                candidate['score'] -= 25
            if 'slider' in img_src or 'slider' in img_alt:
                candidate['score'] -= 20
            
            # Vérifier les dimensions pour éviter les bannières et favoriser les logos typiques
            if img.get('width') and img.get('height'):
                try:
                    width = int(img['width'])
                    height = int(img['height'])
                    
                    # Logos typiques: proportionnés et de taille moyenne
                    if 30 <= width <= 300 and 30 <= height <= 150:
                        candidate['score'] += 15
                    elif width > 500 or height > 300:
                        candidate['score'] -= 25  # Probablement une bannière
                    elif (width < 20 or height < 20) and 'icon' not in candidate['source']:
                        candidate['score'] -= 15  # Probablement une icône de navigation
                    
                    # Les logos ont souvent un ratio largeur/hauteur entre 1:1 et 4:1
                    if width > 0 and height > 0:
                        ratio = width / height
                        if 0.8 <= ratio <= 4.0:
                            candidate['score'] += 10
                        elif ratio > 6.0:  # Très allongé, probablement une bannière
                            candidate['score'] -= 15
                except ValueError:
                    pass
        
        # Méthode 4: Support des favicons ou logos dans les métadonnées comme dernier recours
        meta_logo = soup.select_one('link[rel*="icon"], link[rel="apple-touch-icon"]')
        if meta_logo and meta_logo.get('href'):
            logo_candidates.append({
                'img': meta_logo,
                'score': 5,  # Score faible car c'est un dernier recours
                'source': 'favicon',
                'is_favicon': True
            })
        
        # Si des candidats ont été trouvés, sélectionner le meilleur
        if logo_candidates:
            # Trier par score décroissant
            sorted_candidates = sorted(logo_candidates, key=lambda x: x['score'], reverse=True)
            
            # Prendre le meilleur candidat
            best_candidate = sorted_candidates[0]
            
            # Traiter le cas spécial des favicons
            if best_candidate.get('is_favicon'):
                href = best_candidate['img'].get('href')
                if not href.startswith(('http://', 'https://')):
                    href = urllib.parse.urljoin(url, href)
                return {
                    'type': 'icon',
                    'src': href,
                    'alt': 'Site Icon',
                    'score': best_candidate['score'],
                    'source': best_candidate['source']
                }
            else:
                # Candidate normal (img)
                img = best_candidate['img']
                src = img.get('src')
                if src:
                    # Convertir le chemin relatif en absolu si nécessaire
                    if not src.startswith(('http://', 'https://', 'data:')):
                        src = urllib.parse.urljoin(url, src)
                    
                    return {
                        'type': 'img',
                        'src': src,
                        'alt': img.get('alt', 'Logo'),
                        'width': img.get('width'),
                        'height': img.get('height'),
                        'score': best_candidate['score'],
                        'source': best_candidate['source']
                    }
            
        return None
    
    except Exception as e:
        print(f"Erreur lors de l'extraction du logo: {e}")
        return None

def download_logo(logo_info, output_folder="logos"):
    """
    Télécharge le logo et le sauvegarde localement
    Retourne le chemin du fichier logo
    """
    if not logo_info or not logo_info.get('src'):
        return None
        
    try:
        # Créer le dossier de sortie s'il n'existe pas
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        # Récupérer l'URL du logo
        logo_url = logo_info['src']
        
        # Télécharger l'image
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(logo_url, headers=headers, timeout=20)
        response.raise_for_status()
        
        # Déterminer le format de l'image
        if logo_url.lower().endswith('.png'):
            extension = 'png'
        elif logo_url.lower().endswith('.jpg') or logo_url.lower().endswith('.jpeg'):
            extension = 'jpg'
        elif logo_url.lower().endswith('.svg'):
            extension = 'svg'
        else:
            extension = 'png'  # Par défaut
        
        # Générer un nom de fichier
        domain = urllib.parse.urlparse(logo_url).netloc.split('.')[-2]
        filename = f"{output_folder}/logo_{domain}.{extension}"
        
        # Sauvegarder l'image
        with open(filename, 'wb') as f:
            f.write(response.content)
            
        print(f"Logo sauvegardé: {filename}")
        return filename
        
    except Exception as e:
        print(f"Erreur lors du téléchargement du logo: {e}")
        return None

def extract_main_images(url, max_images=5):
    """
    Extrait les images principales du site web (non-logos, images de grande taille)
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Exclure ces sections qui contiennent généralement des icônes ou éléments de navigation
        exclude_sections = ['nav', 'footer', '.footer', '#footer', '.nav', '#nav', '.navbar', '#navbar']
        for section in exclude_sections:
            for element in soup.select(section):
                element.decompose()
        
        # Trouver les grandes images qui ne sont pas des logos
        main_images = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if not src:
                continue
                
            # Ignorer les images qui ressemblent à des logos ou des icônes
            if re.search(r'logo|icon|favicon', src, re.IGNORECASE):
                continue
                
            # Convertir les URL relatives en absolues
            if not src.startswith(('http://', 'https://', 'data:')):
                src = urllib.parse.urljoin(url, src)
                
            # Vérifier les dimensions si disponibles
            width = img.get('width')
            height = img.get('height')
            if width and height:
                try:
                    if int(width) > 300 or int(height) > 200:
                        main_images.append(src)
                except ValueError:
                    # Si les dimensions ne peuvent pas être converties, inclure l'image quand même
                    main_images.append(src)
            else:
                # Si les dimensions ne sont pas spécifiées, inclure l'image
                main_images.append(src)
                
        # Limiter le nombre d'images retournées
        return main_images[:max_images]
        
    except Exception as e:
        print(f"Erreur lors de l'extraction des images principales: {e}")
        return []

def extract_color_palette(url):
    """
    Extrait une palette de couleurs approximative du site web
    Retourne une liste de couleurs hexadécimales
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extraire les couleurs des styles CSS
        colors = set()
        
        # Recherche des balises style
        for style_tag in soup.find_all('style'):
            if style_tag.string:
                # Recherche de couleurs hexadécimales (#123456)
                hex_colors = re.findall(r'#([0-9a-fA-F]{3,6})', style_tag.string)
                for color in hex_colors:
                    if len(color) == 3:  # Convertir #abc en #aabbcc
                        color = f"#{color[0]}{color[0]}{color[1]}{color[1]}{color[2]}{color[2]}"
                    else:
                        color = f"#{color}"
                    colors.add(color)
                
                # Recherche de couleurs RGB/RGBA
                rgb_colors = re.findall(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', style_tag.string)
                for r, g, b in rgb_colors:
                    hex_color = f"#{int(r):02x}{int(g):02x}{int(b):02x}"
                    colors.add(hex_color)
        
        # Recherche d'attributs de style inline
        for tag in soup.find_all(attrs={'style': True}):
            style = tag['style']
            hex_colors = re.findall(r'#([0-9a-fA-F]{3,6})', style)
            for color in hex_colors:
                if len(color) == 3:  # Convertir #abc en #aabbcc
                    color = f"#{color[0]}{color[0]}{color[1]}{color[1]}{color[2]}{color[2]}"
                else:
                    color = f"#{color}"
                colors.add(color)
                
            rgb_colors = re.findall(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', style)
            for r, g, b in rgb_colors:
                hex_color = f"#{int(r):02x}{int(g):02x}{int(b):02x}"
                colors.add(hex_color)
        
        # Si pas assez de couleurs trouvées, ajouter des couleurs par défaut basées sur des éléments clés
        if len(colors) < 3:
            # Extraire les couleurs d'arrière-plan des éléments principaux
            for element in soup.find_all(['header', 'footer', 'nav', 'main', 'body']):
                if element.has_attr('style') and 'background' in element['style']:
                    style = element['style']
                    hex_colors = re.findall(r'#([0-9a-fA-F]{3,6})', style)
                    for color in hex_colors:
                        if len(color) == 3:
                            color = f"#{color[0]}{color[0]}{color[1]}{color[1]}{color[2]}{color[2]}"
                        else:
                            color = f"#{color}"
                        colors.add(color)
        
        # Si on trouve encore trop peu de couleurs, ajouter des couleurs par défaut
        if len(colors) < 2:
            colors.add("#1a73e8")  # Bleu
            colors.add("#ffffff")  # Blanc
            colors.add("#333333")  # Gris foncé
        
        return list(colors)[:5]  # Limiter à 5 couleurs max
        
    except Exception as e:
        print(f"Erreur lors de l'extraction des couleurs: {e}")
        return ["#1a73e8", "#ffffff", "#333333"]  # Couleurs par défaut