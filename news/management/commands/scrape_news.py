import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from news.models import Article, Category, Tag
from datetime import datetime

class Command(BaseCommand):
    help = 'Scrape news from OnlineKhabar'

    def handle(self, *args, **options):
        self.stdout.write('Starting scraper...')
        
        # 1. Define URL and Categories to look for
        base_url = "https://www.onlinekhabar.com/"
        # Map OnlineKhabar categories to our DB Categories
        # (URL segment : Display Name)
        cat_map = {
            'business': 'Business',
            'sports': 'Sports',
            'entertainment': 'Entertainment',
            'techno': 'Technology',
            'lifestyle': 'Lifestyle',
            'political': 'Politics',
            'society': 'Society' 
        }

        # Create Categories in DB
        for key, name in cat_map.items():
            Category.objects.get_or_create(name=name)
        
        # Also create a 'General' category for others
        general_cat, _ = Category.objects.get_or_create(name='General')

        try:
            response = requests.get(base_url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to fetch site: {e}'))
            return

        # OnlineKhabar Structure (Approximate)
        # They use various classes. We will look for common article containers.
        # Main target: <div class="ok-news-post"> or similar wrapper
        # We will iterate generally over links that look like news
        
        # Logic: Find all 'a' tags, check if they match article pattern
        # Article pattern often: https://www.onlinekhabar.com/2026/01/123456
        
        articles_found = soup.find_all('div', class_='ok-news-post')
        # If specific class not found, try generic item wrapper or fallback to main content
        if not articles_found:
             self.stdout.write('No "ok-news-post" found. Trying generic search...')
             articles_found = soup.find_all('div', class_='item')

        count = 0
        for item in articles_found:
            if count > 20: break # Limit to 20 to avoid timeout
            
            try:
                # 1. Extract Title & Link
                a_tag = item.find('a', href=True)
                if not a_tag: continue
                
                link = a_tag['href']
                title_tag = item.find(['h2', 'h3', 'h4'])
                title = title_tag.get_text(strip=True) if title_tag else a_tag.get_text(strip=True)
                
                if not title or len(title) < 5: continue
                
                # Check for duplicacy
                if Article.objects.filter(title=title).exists():
                    continue

                # 2. Determine Category from Link
                article_cat = general_cat
                for key, name in cat_map.items():
                    if key in link:
                        article_cat = Category.objects.get(name=name)
                        break

                # 3. Extract Image
                img_url = None
                img_tag = item.find('img')
                if img_tag:
                    if 'data-src' in img_tag.attrs:
                        img_url = img_tag['data-src']
                    elif 'src' in img_tag.attrs:
                        img_url = img_tag['src']
                
                # 4. Fetch Article Content (Detail Page)
                # Optimization: For now, just use title as excerpt. 
                # Real scraping would visit 'link' to get full content.
                # Let's try to visit links for the first 5 only to be fast.
                content = "Read full details on OnlineKhabar..."
                excerpt = title[:100] + "..."
                
                if count < 5: 
                    try:
                        art_resp = requests.get(link, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
                        art_soup = BeautifulSoup(art_resp.content, 'html.parser')
                        # OK full content usually in <div class="ok18-single-post-content-wrap">
                        main_content = art_soup.find('div', class_='ok18-single-post-content-wrap')
                        if main_content:
                            paragraphs = main_content.find_all('p')
                            content = "\n\n".join([p.get_text() for p in paragraphs])
                            if paragraphs:
                                excerpt = paragraphs[0].get_text()[:200]
                    except:
                        pass # Fallback to default content

                # 5. Save to DB
                article = Article(
                    title=title,
                    slug=slugify(title[:30] + "-" + str(datetime.now().timestamp())),
                    # If title is Nepali, slugify might be empty. OK URLs usually satisfy this.
                    # We will use a fallback slug if necessary
                    category=article_cat,
                    content=content,
                    excerpt=excerpt,
                    status='published',
                    views=0
                )
                
                if not article.slug:
                    article.slug = f"news-{datetime.now().timestamp()}-{count}"

                if img_url:
                    try:
                        img_resp = requests.get(img_url, timeout=5)
                        if img_resp.status_code == 200:
                            file_name = f"news_{count}.jpg"
                            article.image.save(file_name, ContentFile(img_resp.content), save=False)
                    except:
                        pass # Skip image if fail

                article.save()
                self.stdout.write(self.style.SUCCESS(f'Saved: {title[:30]}...'))
                count += 1
                
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error processing item: {e}'))
                continue

        self.stdout.write(self.style.SUCCESS(f'Successfully scraped {count} articles.'))
