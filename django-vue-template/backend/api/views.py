from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Message, MessageSerializer
from pathlib import Path
import numpy as np
import pandas as pd
import clip
import torch
import os


# Serve Vue Application
index_view = never_cache(TemplateView.as_view(template_name='index.html'))


class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows messages to be viewed or edited.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer




@api_view(['GET'])
def search_images(request):
    keyword = request.GET.get('keyword')
    number = int(request.GET.get('number'))
    result = search(number, keyword)
    print(result)
    response = Response({'result': result})
    response["Access-Control-Allow-Origin"] = "*"
    return response


def search(num, keyword):
    # Set the paths
    BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    photos_path = os.path.join(BASE_DIR, 'media', 'image_dataset', 'image_dataset')
    features_path = os.path.join(BASE_DIR, 'media', 'image_dataset', 'features')
    print(photos_path)
    # Read the photos table
    # photos = pd.read_csv(unsplash_dataset_path / "photos.tsv000", sep='\t', header=0)

    # Load the features and the corresponding IDs
    photo_features = np.load(features_path + "/features.npy")
    photo_ids = pd.read_csv(features_path + "/photo_ids.csv")
    photo_ids = list(photo_ids['photo_id'])
    model_path = os.path.join(BASE_DIR, 'media')
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load(model_path+"/ViT-B-32.pt", device=device)
    
    search_query = keyword
    print(keyword)
    with torch.no_grad():
        # Encode and normalize the description using CLIP
        text_encoded = model.encode_text(clip.tokenize(search_query).to(device))
        text_encoded /= text_encoded.norm(dim=-1, keepdim=True)
    
    # Retrieve the description vector and the photo vectors
    text_features = text_encoded.cpu().numpy()

    # Compute the similarity between the descrption and each photo using the Cosine similarity
    similarities = list((text_features @ photo_features.T).squeeze(0))

    # Sort the photos by their similarity score
    best_photos = sorted(zip(similarities, range(photo_features.shape[0])), key=lambda x: x[0], reverse=True)
    ret = []
    for i in range(num):
    # Retrieve the photo ID
        idx = best_photos[i][1]
        photo_id = photo_ids[idx]
        print(photo_id)
        image_path = "image_dataset/image_dataset/" + photo_id + ".png"
        ret.append(image_path)
    return ret