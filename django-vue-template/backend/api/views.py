from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Message, MessageSerializer
from PIL import Image
from pathlib import Path
import numpy as np
import pandas as pd
import clip
import torch
import os
import torch
from io import BytesIO
import math

feature_batch = 193

# Serve Vue Application
index_view = never_cache(TemplateView.as_view(template_name='index.html'))


class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows messages to be viewed or edited.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer



@api_view(['POST'])
def upload_images(request):
    new_image_file_list = request.FILES.getlist('file_list')
    print(type(new_image_file_list))
    photos_files = []
    for new_image_file in new_image_file_list:
        print(new_image_file.name)
        print(new_image_file.size)
        BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        photos_path = os.path.join(BASE_DIR, 'media', 'image_dataset', 'image_dataset')
        new_image = Image.open(new_image_file)
        new_name = photos_path+"/"+new_image_file.name.split(".")[0] + ".png"
        new_image.save(new_name)
        photos_files.append(Path(new_name))

    calculate_feature(photos_files)
    response = Response({'return':"ok"})
    response["Access-Control-Allow-Origin"] = "*"
    return response


def calculate_feature(photos_files):
    BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    device = "cpu"
    model_path = os.path.join(BASE_DIR, 'media')
    model, preprocess = clip.load(model_path+"/ViT-B-32.pt", device=device)
    batch_size = 16
    photos_path = os.path.join(BASE_DIR, 'media', 'image_dataset', 'image_dataset')
    features_path = os.path.join(BASE_DIR, 'media', 'image_dataset', 'features')
    features_path = Path(features_path)
    batches = math.ceil(len(photos_files) / batch_size)
    print()
    for i in range(batches):
        print(f"Processing batch {i+1}/{batches}")
        global feature_batch
        batch_ids_path = os.path.join(features_path, f"{(i+feature_batch):010d}.csv")
        batch_features_path =os.path.join(features_path, f"{(i+feature_batch):010d}.npy")
        batch_ids_path = Path(batch_ids_path)
        batch_features_path = Path(batch_features_path)

        features_list = []
        features_list.append(np.load(features_path / "features.npy"))
        photo_ids_list = []
        photo_ids_list.append(pd.read_csv(features_path / "photo_ids.csv"))

        # Only do the processing if the batch wasn't processed yet
        if not batch_features_path.exists():
            try:
                # Select the photos for the current batch
                batch_files = photos_files[i*batch_size : (i+1)*batch_size]
                print(batch_features_path)

                # Compute the features and save to a numpy file
                batch_features = compute_clip_features(model, preprocess, batch_files)
                np.save(batch_features_path, batch_features)
                features_list.append(batch_features)
                # Save the photo IDs to a CSV file
                photo_ids = [photo_file.name.split(".")[0] for photo_file in batch_files]
                photo_ids_data = pd.DataFrame(photo_ids, columns=['photo_id'])
                photo_ids_data.to_csv(batch_ids_path, index=False)
                photo_ids_list.append(pd.read_csv(batch_ids_path))
            except:
                # Catch problems with the processing to make the process more robust
                print(f'Problem with batch {i}')
    feature_batch = feature_batch + batches
    print(feature_batch)
    # Concatenate the features and store in a merged file
    features = np.concatenate(features_list)
    np.save(features_path / "features.npy", features)
    # Load all the photo IDs
    photo_ids = pd.concat(photo_ids_list)
    photo_ids.to_csv(features_path / "photo_ids.csv", index=False)


def compute_clip_features(model, preprocess, photos_batch):
    # Load all the photos from the files
    device = "cuda" if torch.cuda.is_available() else "cpu"
    photos = [Image.open(photo_file) for photo_file in photos_batch]
    # Preprocess all photos
    photos_preprocessed = torch.stack([preprocess(photo) for photo in photos]).to(device)
    with torch.no_grad():
        # Encode the photos batch to compute the feature vectors and normalize them
        photos_features = model.encode_image(photos_preprocessed)
        photos_features /= photos_features.norm(dim=-1, keepdim=True)
    # Transfer the feature vectors back to the CPU and convert to numpy
    return photos_features.cpu().numpy()



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