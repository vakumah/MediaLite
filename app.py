import streamlit as st
import ffmpeg
import os
import tempfile
import time
from datetime import datetime
from PIL import Image, ImageEnhance, ImageFilter
import io

# ══════════════════════════════════════════════════════════════════════════════
# APP CONFIG
# ══════════════════════════════════════════════════════════════════════════════

APP_NAME = "MediaLite"
APP_VERSION = "3.1.0"

MAX_VIDEO_SIZE_MB = 500
MAX_IMAGE_SIZE_MB = 50
TARGET_SIZE_KB = 950

# ══════════════════════════════════════════════════════════════════════════════
# TRANSLATIONS
# ══════════════════════════════════════════════════════════════════════════════

TRANSLATIONS = {
    "en": {
        "tagline": "Compress & enhance your media",
        "video": "Video",
        "photo": "Photo",
        "enhance": "Enhance",
        "under_1mb": "<1MB",
        "drop_video": "Drop video here",
        "drop_image": "Drop image here",
        "size": "Size",
        "resolution": "Resolution",
        "duration": "Duration",
        "settings": "Settings",
        "output_resolution": "Resolution",
        "enhance_sharpness": "Enhance sharpness",
        "target_size": "Target size (KB)",
        "remove_audio": "Remove audio",
        "sharpness": "Sharpness",
        "compress_video": "Compress Video",
        "process_photo": "Process Photo",
        "processing": "Processing...",
        "compressing": "Compressing and enhancing",
        "enhancing": "Enhancing and compressing",
        "done": "Done!",
        "original": "Original",
        "compressed": "Compressed",
        "enhanced": "Enhanced",
        "dimensions": "Dimensions",
        "smaller": "smaller",
        "download": "Download",
        "failed": "Processing failed",
        "try_different": "Try different settings",
        "file_too_large": "File too large",
        "max_size": "Maximum size",
        "quality": "Quality",
        "speed": "Speed",
        "faster": "Faster",
        "balanced": "Balanced",
        "best": "Best Quality",
        "details": "Details",
        "made_by": "Made with ❤️ by",
        "license": "GPL-3.0 License",
        "supports": "Supports JPG, PNG, WebP, HEIC (Live Photo), and more",
        "max_500mb": "Max 500MB",
    },
    "id": {
        "tagline": "Kompres & tingkatkan kualitas media",
        "video": "Video",
        "photo": "Foto",
        "enhance": "Tingkatkan",
        "under_1mb": "<1MB",
        "drop_video": "Taruh video di sini",
        "drop_image": "Taruh gambar di sini",
        "size": "Ukuran",
        "resolution": "Resolusi",
        "duration": "Durasi",
        "settings": "Pengaturan",
        "output_resolution": "Resolusi",
        "enhance_sharpness": "Tingkatkan ketajaman",
        "target_size": "Target ukuran (KB)",
        "remove_audio": "Hapus audio",
        "sharpness": "Ketajaman",
        "compress_video": "Kompres Video",
        "process_photo": "Proses Foto",
        "processing": "Memproses...",
        "compressing": "Mengompres dan meningkatkan kualitas",
        "enhancing": "Meningkatkan dan mengompres",
        "done": "Selesai!",
        "original": "Asli",
        "compressed": "Terkompres",
        "enhanced": "Ditingkatkan",
        "dimensions": "Dimensi",
        "smaller": "lebih kecil",
        "download": "Unduh",
        "failed": "Pemrosesan gagal",
        "try_different": "Coba pengaturan lain",
        "file_too_large": "File terlalu besar",
        "max_size": "Ukuran maksimal",
        "quality": "Kualitas",
        "speed": "Kecepatan",
        "faster": "Lebih Cepat",
        "balanced": "Seimbang",
        "best": "Kualitas Terbaik",
        "details": "Detail",
        "made_by": "Dibuat dengan ❤️ oleh",
        "license": "Lisensi GPL-3.0",
        "supports": "Mendukung JPG, PNG, WebP, HEIC (Live Photo), dan lainnya",
        "max_500mb": "Maks 500MB",
    }
}

def t(key):
    """Get translation for current language"""
    lang = st.session_state.get('language', 'en')
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)

st.set_page_config(
    page_title=f"{APP_NAME} - Media Compressor",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize language
if 'language' not in st.session_state:
    st.session_state.language = 'en'

# ══════════════════════════════════════════════════════════════════════════════
# CUSTOM CSS
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary: #6366f1;
        --primary-hover: #818cf8;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --surface: #1e1e2e;
        --surface-2: #2a2a3e;
        --surface-3: #363650;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --border: #404060;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    .main-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
        margin-bottom: 1rem;
    }
    
    .main-header h1 {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .main-header p {
        color: var(--text-secondary);
        font-size: 1.1rem;
        font-weight: 400;
    }
    
    .lang-selector {
        position: absolute;
        top: 1rem;
        right: 1rem;
        z-index: 1000;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.75rem;
        margin: 1.5rem 0;
    }
    
    .feature-item {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }
    
    .feature-icon {
        font-size: 1.3rem;
        margin-bottom: 0.4rem;
    }
    
    .feature-text {
        color: var(--text-secondary);
        font-size: 0.8rem;
    }
    
    .stats-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.25rem;
        margin: 0.5rem 0;
    }
    
    .stats-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 0;
        border-bottom: 1px solid var(--border);
    }
    
    .stats-row:last-child {
        border-bottom: none;
    }
    
    .stats-label {
        color: var(--text-secondary);
        font-size: 0.9rem;
    }
    
    .stats-value {
        color: var(--text-primary);
        font-weight: 600;
        font-size: 1rem;
    }
    
    .reduction-badge {
        background: linear-gradient(135deg, var(--success), #059669);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        display: inline-block;
        margin-top: 0.5rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.875rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4) !important;
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.875rem 2rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3) !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: var(--surface);
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        color: var(--text-secondary);
        padding: 0.75rem 1.5rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
    }
    
    .stSlider > div > div {
        background-color: var(--surface-3) !important;
    }
    
    .stSlider > div > div > div > div {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    }
    
    .stSelectbox > div > div, .stRadio > div {
        background-color: var(--surface) !important;
        border-color: var(--border) !important;
        border-radius: 10px !important;
    }
    
    .stCheckbox > label {
        color: var(--text-primary) !important;
    }
    
    .stExpander {
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
    }
    
    .stProgress > div > div {
        background: linear-gradient(135deg, #6366f1, #a855f7) !important;
    }
    
    .success-box {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.1));
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .error-box {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .processing-status {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        text-align: center;
    }
    
    .processing-status h3 {
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    
    .processing-status p {
        color: var(--text-secondary);
        font-size: 0.9rem;
    }
    
    .footer {
        text-align: center;
        padding: 2rem 0;
        margin-top: 2rem;
        border-top: 1px solid var(--border);
    }
    
    .footer p {
        color: var(--text-secondary);
        font-size: 0.85rem;
    }
    
    .stFileUploader > div {
        background-color: var(--surface) !important;
        border: 2px dashed var(--border) !important;
        border-radius: 16px !important;
    }
    
    .stFileUploader > div:hover {
        border-color: var(--primary) !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    div[data-testid="stToolbar"] {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def format_duration(seconds):
    if seconds < 3600:
        return time.strftime('%M:%S', time.gmtime(seconds))
    return time.strftime('%H:%M:%S', time.gmtime(seconds))

def get_video_info(file_path):
    try:
        probe = ffmpeg.probe(file_path)
        video_info = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
        audio_info = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)
        
        if video_info:
            width = int(video_info.get('width', 0))
            height = int(video_info.get('height', 0))
            duration = float(probe['format'].get('duration', 0))
            fps = eval(video_info.get('r_frame_rate', '0/1'))
            fps = round(fps, 2) if fps else 0
            
            return {
                'width': width,
                'height': height,
                'duration': duration,
                'fps': fps,
                'has_audio': audio_info is not None
            }
    except Exception:
        pass
    return None

def cleanup_temp_files(*paths):
    for path in paths:
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except Exception:
            pass

# ══════════════════════════════════════════════════════════════════════════════
# IMAGE PROCESSING ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def enhance_image(img, sharpness=1.3, contrast=1.1, saturation=1.05):
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(sharpness)
    
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(contrast)
    
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(saturation)
    
    return img

def compress_image_to_target(img, target_kb=950, min_quality=40, output_format='JPEG'):
    if img.mode in ('RGBA', 'P', 'LA'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    
    low, high = min_quality, 95
    best_buffer = None
    best_quality = high
    
    while low <= high:
        mid = (low + high) // 2
        buffer = io.BytesIO()
        
        save_kwargs = {'format': output_format, 'quality': mid, 'optimize': True}
        if output_format == 'JPEG':
            save_kwargs['progressive'] = True
        
        img.save(buffer, **save_kwargs)
        size_kb = buffer.tell() / 1024
        
        if size_kb <= target_kb:
            best_buffer = buffer
            best_quality = mid
            low = mid + 1
        else:
            high = mid - 1
    
    if best_buffer is None or best_buffer.tell() / 1024 > target_kb:
        scale = 0.9
        temp_img = img.copy()
        
        while scale > 0.3:
            new_size = (int(temp_img.width * scale), int(temp_img.height * scale))
            resized = img.resize(new_size, Image.Resampling.LANCZOS)
            
            buffer = io.BytesIO()
            save_kwargs = {'format': output_format, 'quality': 85, 'optimize': True}
            if output_format == 'JPEG':
                save_kwargs['progressive'] = True
            
            resized.save(buffer, **save_kwargs)
            
            if buffer.tell() / 1024 <= target_kb:
                best_buffer = buffer
                break
            
            scale -= 0.1
        
        if best_buffer is None:
            best_buffer = buffer
    
    best_buffer.seek(0)
    return best_buffer, best_buffer.tell()

def process_image(input_bytes, enhance=True, sharpness=1.3, target_kb=950):
    try:
        img = Image.open(io.BytesIO(input_bytes))
        original_size = img.size
        
        if enhance:
            img = enhance_image(img, sharpness=sharpness)
        
        output_buffer, final_size = compress_image_to_target(img, target_kb=target_kb)
        
        final_img = Image.open(output_buffer)
        final_dimensions = final_img.size
        output_buffer.seek(0)
        
        return {
            'success': True,
            'data': output_buffer.getvalue(),
            'original_size': original_size,
            'final_size': final_dimensions,
            'file_size': final_size
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

# ══════════════════════════════════════════════════════════════════════════════
# VIDEO COMPRESSION ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def calculate_target_bitrate(duration_seconds, target_size_kb=950):
    target_bits = target_size_kb * 8 * 1024
    bitrate = int(target_bits / duration_seconds)
    return max(bitrate, 100000)

def compress_video(input_path, output_path, config):
    try:
        target_size_kb = config.get('target_size_kb', 950)
        remove_audio = config.get('remove_audio', False)
        target_res = config.get('resolution', '480p')
        enhance = config.get('enhance', True)
        
        video_info = get_video_info(input_path)
        duration = video_info['duration'] if video_info else 30
        
        audio_bitrate = 64000 if not remove_audio else 0
        video_target_kb = target_size_kb - (audio_bitrate * duration / 8 / 1024)
        video_target_kb = max(video_target_kb, target_size_kb * 0.7)
        
        target_bitrate = calculate_target_bitrate(duration, video_target_kb)
        
        input_stream = ffmpeg.input(input_path)
        video = input_stream.video
        audio = input_stream.audio
        
        scale_map = {
            '720p': ('trunc(oh*a/2)*2', 720),
            '480p': ('trunc(oh*a/2)*2', 480),
            '360p': ('trunc(oh*a/2)*2', 360),
            '240p': ('trunc(oh*a/2)*2', 240)
        }
        
        if target_res in scale_map:
            w, h = scale_map[target_res]
            video = ffmpeg.filter(video, 'scale', w, h)
        else:
            video = ffmpeg.filter(video, 'scale', 'trunc(iw/2)*2', 'trunc(ih/2)*2')
        
        if enhance:
            video = ffmpeg.filter(video, 'unsharp', '5:5:0.8:3:3:0.4')
            video = ffmpeg.filter(video, 'eq', contrast=1.05, saturation=1.1)
        
        video_params = {
            'vcodec': 'libx264',
            'b:v': target_bitrate,
            'maxrate': int(target_bitrate * 1.5),
            'bufsize': int(target_bitrate * 2),
            'preset': 'medium',
            'pix_fmt': 'yuv420p',
            'colorspace': 'bt709',
            'color_primaries': 'bt709',
            'color_trc': 'bt709',
            'color_range': 'tv',
            'movflags': '+faststart',
            'profile:v': 'high',
            'level:v': '4.1',
        }
        
        if remove_audio:
            output = ffmpeg.output(video, output_path, **video_params, an=None)
        else:
            audio_params = {'c:a': 'aac', 'b:a': '64k', 'ar': 44100, 'ac': 1}
            output = ffmpeg.output(audio, video, output_path, **audio_params, **video_params)
        
        ffmpeg.run(output, overwrite_output=True, capture_stdout=True, capture_stderr=True)
        
        if os.path.exists(output_path):
            final_size = os.path.getsize(output_path)
            if final_size > target_size_kb * 1024 * 1.1:
                new_bitrate = int(target_bitrate * (target_size_kb * 1024 / final_size) * 0.9)
                video_params['b:v'] = new_bitrate
                video_params['maxrate'] = int(new_bitrate * 1.5)
                video_params['bufsize'] = int(new_bitrate * 2)
                
                if remove_audio:
                    output = ffmpeg.output(video, output_path, **video_params, an=None)
                else:
                    output = ffmpeg.output(audio, video, output_path, **audio_params, **video_params)
                
                ffmpeg.run(output, overwrite_output=True, capture_stdout=True, capture_stderr=True)
        
        return True, None
        
    except ffmpeg.Error as e:
        error_msg = e.stderr.decode('utf8') if e.stderr else str(e)
        return False, error_msg
    except Exception as e:
        return False, str(e)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN UI
# ══════════════════════════════════════════════════════════════════════════════

def main():
    # Language selector at top
    col_spacer, col_lang = st.columns([5, 1])
    with col_lang:
        lang_options = {"🇺🇸 EN": "en", "🇮🇩 ID": "id"}
        current_lang = "🇺🇸 EN" if st.session_state.language == "en" else "🇮🇩 ID"
        selected = st.selectbox(
            "Lang",
            options=list(lang_options.keys()),
            index=0 if st.session_state.language == "en" else 1,
            label_visibility="collapsed"
        )
        if lang_options[selected] != st.session_state.language:
            st.session_state.language = lang_options[selected]
            st.rerun()
    
    # Header
    st.markdown(f"""
        <div class="main-header">
            <h1>🎬 {APP_NAME}</h1>
            <p>{t('tagline')}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Feature highlights
    st.markdown(f"""
        <div class="feature-grid">
            <div class="feature-item">
                <div class="feature-icon">📹</div>
                <div class="feature-text">{t('video')}</div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">📷</div>
                <div class="feature-text">{t('photo')}</div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">✨</div>
                <div class="feature-text">{t('enhance')}</div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">📱</div>
                <div class="feature-text">{t('under_1mb')}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Tabs
    tab_video, tab_photo = st.tabs([f"🎬 {t('video')}", f"📷 {t('photo')}"])
    
    # ══════════════════════════════════════════════════════════════════════════
    # VIDEO TAB
    # ══════════════════════════════════════════════════════════════════════════
    
    with tab_video:
        video_file = st.file_uploader(
            t('drop_video'),
            type=["mp4", "mov", "mkv", "avi", "webm", "3gp"],
            key="video_uploader",
            help=t('max_500mb')
        )
        
        if video_file is not None:
            file_size = len(video_file.getvalue())
            if file_size > MAX_VIDEO_SIZE_MB * 1024 * 1024:
                st.error(f"{t('file_too_large')}. {t('max_size')} {MAX_VIDEO_SIZE_MB}MB")
                return
            
            temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            temp_input.write(video_file.read())
            temp_input.close()
            input_path = temp_input.name
            
            original_size = os.path.getsize(input_path)
            video_info = get_video_info(input_path)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(t('size'), format_size(original_size))
            with col2:
                if video_info:
                    st.metric(t('resolution'), f"{video_info['width']}×{video_info['height']}")
            with col3:
                if video_info:
                    st.metric(t('duration'), format_duration(video_info['duration']))
            
            with st.expander(f"⚙️ {t('settings')}", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    resolution = st.selectbox(
                        t('output_resolution'),
                        ["480p", "360p", "240p", "720p"],
                        index=0,
                        key="video_res"
                    )
                    enhance_video = st.checkbox(t('enhance_sharpness'), value=True, key="video_enhance")
                
                with col2:
                    target_size = st.slider(
                        t('target_size'),
                        min_value=200,
                        max_value=950,
                        value=900,
                        step=50,
                        key="video_target"
                    )
                    remove_audio = st.checkbox(t('remove_audio'), value=False, key="video_mute")
            
            if st.button(f"🚀 {t('compress_video')}", key="compress_video", use_container_width=True):
                output_path = input_path.replace('.mp4', '_out.mp4')
                
                progress = st.progress(0)
                status = st.empty()
                
                status.markdown(f"""
                    <div class="processing-status">
                        <h3>🔄 {t('processing')}</h3>
                        <p>{t('compressing')}</p>
                    </div>
                """, unsafe_allow_html=True)
                progress.progress(30)
                
                config = {
                    'target_size_kb': target_size,
                    'remove_audio': remove_audio,
                    'resolution': resolution,
                    'enhance': enhance_video
                }
                
                success, error = compress_video(input_path, output_path, config)
                
                if success and os.path.exists(output_path):
                    progress.progress(100)
                    final_size = os.path.getsize(output_path)
                    reduction = ((original_size - final_size) / original_size) * 100
                    
                    status.empty()
                    progress.empty()
                    
                    st.markdown(f"""
                        <div class="success-box">
                            <h3 style="color: #10b981;">✅ {t('done')}</h3>
                            <div class="stats-row">
                                <span class="stats-label">{t('original')}</span>
                                <span class="stats-value">{format_size(original_size)}</span>
                            </div>
                            <div class="stats-row">
                                <span class="stats-label">{t('compressed')}</span>
                                <span class="stats-value">{format_size(final_size)}</span>
                            </div>
                            <div style="text-align: center; margin-top: 1rem;">
                                <span class="reduction-badge">📉 {reduction:.1f}% {t('smaller')}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.video(output_path)
                    
                    with open(output_path, "rb") as f:
                        st.download_button(
                            f"⬇️ {t('download')}",
                            f,
                            file_name=f"compressed_{datetime.now().strftime('%H%M%S')}.mp4",
                            mime="video/mp4",
                            use_container_width=True
                        )
                    
                    cleanup_temp_files(output_path)
                else:
                    progress.empty()
                    status.empty()
                    st.error(f"{t('failed')}. {t('try_different')}")
                    if error:
                        with st.expander(t('details')):
                            st.code(error[:300])
    
    # ══════════════════════════════════════════════════════════════════════════
    # PHOTO TAB
    # ══════════════════════════════════════════════════════════════════════════
    
    with tab_photo:
        image_file = st.file_uploader(
            t('drop_image'),
            type=["jpg", "jpeg", "png", "webp", "heic", "heif", "bmp", "tiff", "gif"],
            key="image_uploader",
            help=t('supports')
        )
        
        if image_file is not None:
            original_bytes = image_file.getvalue()
            original_size = len(original_bytes)
            
            try:
                original_img = Image.open(io.BytesIO(original_bytes))
                original_dimensions = original_img.size
            except Exception as e:
                st.error(f"{t('failed')}: {e}")
                return
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(t('size'), format_size(original_size))
            with col2:
                st.metric(t('resolution'), f"{original_dimensions[0]}×{original_dimensions[1]}")
            
            with st.expander(f"⚙️ {t('settings')}", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    enhance_photo = st.checkbox(t('enhance_sharpness'), value=True, key="photo_enhance")
                    sharpness_level = st.slider(
                        t('sharpness'),
                        min_value=1.0,
                        max_value=2.0,
                        value=1.4,
                        step=0.1,
                        key="sharpness",
                        disabled=not enhance_photo
                    )
                
                with col2:
                    target_kb = st.slider(
                        t('target_size'),
                        min_value=100,
                        max_value=950,
                        value=800,
                        step=50,
                        key="photo_target"
                    )
            
            if st.button(f"🚀 {t('process_photo')}", key="process_photo", use_container_width=True):
                progress = st.progress(0)
                status = st.empty()
                
                status.markdown(f"""
                    <div class="processing-status">
                        <h3>🔄 {t('processing')}</h3>
                        <p>{t('enhancing')}</p>
                    </div>
                """, unsafe_allow_html=True)
                progress.progress(30)
                
                result = process_image(
                    original_bytes,
                    enhance=enhance_photo,
                    sharpness=sharpness_level if enhance_photo else 1.0,
                    target_kb=target_kb
                )
                
                if result['success']:
                    progress.progress(100)
                    final_size = result['file_size']
                    reduction = ((original_size - final_size) / original_size) * 100
                    
                    status.empty()
                    progress.empty()
                    
                    st.markdown(f"""
                        <div class="success-box">
                            <h3 style="color: #10b981;">✅ {t('done')}</h3>
                            <div class="stats-row">
                                <span class="stats-label">{t('original')}</span>
                                <span class="stats-value">{format_size(original_size)}</span>
                            </div>
                            <div class="stats-row">
                                <span class="stats-label">{t('compressed')}</span>
                                <span class="stats-value">{format_size(final_size)}</span>
                            </div>
                            <div class="stats-row">
                                <span class="stats-label">{t('dimensions')}</span>
                                <span class="stats-value">{result['final_size'][0]}×{result['final_size'][1]}</span>
                            </div>
                            <div style="text-align: center; margin-top: 1rem;">
                                <span class="reduction-badge">📉 {reduction:.1f}% {t('smaller')}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.caption(t('original'))
                        st.image(original_bytes, use_container_width=True)
                    with col2:
                        st.caption(t('enhanced'))
                        st.image(result['data'], use_container_width=True)
                    
                    st.download_button(
                        f"⬇️ {t('download')}",
                        result['data'],
                        file_name=f"enhanced_{datetime.now().strftime('%H%M%S')}.jpg",
                        mime="image/jpeg",
                        use_container_width=True
                    )
                else:
                    progress.empty()
                    status.empty()
                    st.error(f"{t('failed')}: {result.get('error', 'Unknown error')}")
    
    # Footer
    st.markdown(f"""
        <div class="footer">
            <p style="font-size: 1rem; margin-bottom: 0.5rem;">{t('made_by')} <strong>Fiki</strong></p>
            <p>{APP_NAME} v{APP_VERSION} • {t('license')}</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()