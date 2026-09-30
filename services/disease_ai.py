import base64
import json
import mimetypes
import urllib.request


def _fallback(symptoms):
    s = (symptoms or '').lower()
    hints = []
    if any(x in s for x in ['cough', 'coughing', 'inkorora']):
        hints.append(('Respiratory illness', 'Respiratory infection, irritation or another respiratory condition may be possible.'))
    if any(x in s for x in ['diarrhea', 'diarrhoea', 'impiswi']):
        hints.append(('Digestive disorder', 'Digestive infection, parasites, feed change or contaminated water may be possible.'))
    if any(x in s for x in ['fever', 'hot body', 'umuriro']):
        hints.append(('Fever / systemic illness', 'Fever can accompany several infections and requires veterinary assessment.'))
    if any(x in s for x in ['not eating', 'loss of appetite', 'appetite', 'kutarya']):
        hints.append(('Reduced appetite', 'Reduced appetite can result from pain, infection, digestive problems, poor feed or other illness.'))
    if any(x in s for x in ['swollen', 'swelling', 'kubyimba']):
        hints.append(('Inflammation / injury', 'Swelling can have infectious, traumatic or inflammatory causes.'))
    if not hints:
        hints.append(('Insufficient evidence', 'One symptom alone is not enough to identify a disease reliably. More history and examination are needed.'))
    return {
        'assessment': hints,
        'confidence': 'Preliminary only',
        'warning': 'This is decision support, not a veterinary diagnosis. A veterinarian should examine the cow, especially when symptoms are severe, persistent or rapidly worsening.',
        'next_steps': ['Isolate a visibly sick cow when appropriate to reduce transmission risk.', 'Provide clean water and normal supportive care.', 'Record temperature and other observable changes if you can do so safely.', 'Contact a qualified veterinarian for diagnosis and treatment.']
    }


def analyze_cow(symptoms, image_path=None, api_key=None, model='gpt-5.6-luna'):
    if not api_key:
        return _fallback(symptoms)
    content=[{'type':'input_text','text':(
        'Analyze this cow health case as veterinary decision support. '
        'Symptoms reported: ' + (symptoms or 'none provided') + '\n'
        'If an image is provided, describe only visible signs. Give a short list of possible conditions, '
        'why they may fit, what additional information a veterinarian needs, and urgent warning signs. '
        'Do not claim a confirmed diagnosis. Recommend professional veterinary examination for treatment decisions.'
    )}]
    if image_path:
        mime=mimetypes.guess_type(image_path)[0] or 'image/jpeg'
        with open(image_path,'rb') as f:
            data=base64.b64encode(f.read()).decode('ascii')
        content.append({'type':'input_image','image_url':f'data:{mime};base64,{data}'})
    payload={'model':model,'input':[{'role':'user','content':content}],'max_output_tokens':1000}
    req=urllib.request.Request('https://api.openai.com/v1/responses', data=json.dumps(payload).encode(), headers={'Content-Type':'application/json','Authorization':f'Bearer {api_key}'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data=json.loads(r.read().decode())
        text=data.get('output_text')
        if text:
            return {'assessment':[('AI veterinary assessment', text.strip())], 'confidence':'AI preliminary assessment', 'warning':'AI cannot confirm a disease from symptoms or an image. Veterinary examination is required for diagnosis and treatment.', 'next_steps':['Compare the assessment with the cow\'s recent health history.','Seek qualified veterinary care for diagnosis and treatment.']}
    except Exception as exc:
        print(f'Disease AI error: {exc}')
    return _fallback(symptoms)
