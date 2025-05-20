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
    Extrait le logo d'un site web en utilisant plusieurs méthodes
    Retourne un dictionnaire avec les informations du logo ou None si aucun logo n'est trouvé
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Méthode 1: Recherche par attributs communs des logos
        logo_candidates = []
        
        # Chercher dans les balises img avec des mots-clés communs dans le chemin ou les attributs
        logo_patterns = [r'logo', r'brand', r'header-image', r'site-icon']
        for img in soup.find_all('img'):
            img_src = img.get('src', '')
            img_alt = img.get('alt', '')
            img_class = ' '.join(img.get('class', []))
            img_id = img.get('id', '')
            
            # Vérifier si l'une des caractéristiques de l'image contient un pattern de logo
            for pattern in logo_patterns:
                if (re.search(pattern, img_src, re.IGNORECASE) or 
                    re.search(pattern, img_alt, re.IGNORECASE) or 
                    re.search(pattern, img_class, re.IGNORECASE) or
                    re.search(pattern, img_id, re.IGNORECASE)):
                    logo_candidates.append(img)
                    break
        
        # Méthode 2: Vérifier les zones communes où se trouvent les logos
        header_logo = soup.select_one('header img, .header img, #header img')
        if header_logo:
            logo_candidates.append(header_logo)
            
        navbar_logo = soup.select_one('nav img, .navbar img, .nav img')
        if navbar_logo:
            logo_candidates.append(navbar_logo)
        
        # Méthode 3: Chercher la première image dans l'en-tête
        header = soup.find(['header', 'div'], {'class': ['header', 'navbar', 'nav', 'top']})
        if header:
            first_img = header.find('img')
            if first_img:
                logo_candidates.append(first_img)
            
        # Si des candidats ont été trouvés, sélectionner le meilleur
        if logo_candidates:
            # Dédupliquer les candidats
            unique_candidates = []
            seen_srcs = set()
            for img in logo_candidates:
                src = img.get('src', '')
                if src and src not in seen_srcs:
                    seen_srcs.add(src)
                    unique_candidates.append(img)
            
            # Prioritiser les images avec la meilleure résolution ou taille appropriée pour un logo
            best_candidate = max(unique_candidates, key=lambda img: score_logo_candidate(img, url))
            
            # Convertir le chemin relatif en absolu si nécessaire
            src = best_candidate.get('src')
            if src:
                if not src.startswith(('http://', 'https://', 'data:')):
                    src = urllib.parse.urljoin(url, src)
                
                return {
                    'type': 'img',
                    'src': src,
                    'alt': best_candidate.get('alt', 'Logo'),
                    'width': best_candidate.get('width'),
                    'height': best_candidate.get('height')
                }
            
        # Méthode alternative: rechercher dans les métadonnées
        meta_logo = soup.select_one('link[rel*="icon"], link[rel="apple-touch-icon"]')
        if meta_logo and meta_logo.get('href'):
            href = meta_logo.get('href')
            if not href.startswith(('http://', 'https://')):
                href = urllib.parse.urljoin(url, href)
            return {
                'type': 'icon',
                'src': href,
                'alt': 'Site Icon'
            }
            
        return None
    
    except Exception as e:
        print(f"Erreur lors de l'extraction du logo: {e}")
        return None

def score_logo_candidate(img, site_url):
    """Attribue un score au candidat logo basé sur différents facteurs"""
    score = 0
    
    # Les logos sont généralement en haut de page
    if img.find_parent(['header', 'nav']):
        score += 20
    
    # Les logos contiennent souvent le nom du site
    domain = urllib.parse.urlparse(site_url).netloc.split('.')[-2]
    img_alt = img.get('alt', '').lower()
    img_src = img.get('src', '').lower()
    if domain.lower() in img_alt or domain.lower() in img_src:
        score += 15
    
    # Pénaliser les images trop grandes (banners) ou trop petites (icônes de navigation)
    if img.get('width') and img.get('height'):
        try:
            width = int(img['width'])
            height = int(img['height'])
            
            # Logos typiques: entre 30x30 et 300x200
            if 30 <= width <= 300 and 30 <= height <= 200:
                score += 10
            elif width > 500 or height > 500:
                score -= 10
            elif width < 20 or height < 20:
                score -= 5
        except ValueError:
            pass
            
    return score

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
        response = requests.get(logo_url, headers=headers, timeout=10)
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
        response = requests.get(url, headers=headers, timeout=10)
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
        response = requests.get(url, headers=headers, timeout=10)
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