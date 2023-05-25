<template>
  <div>
    <div>
      <input multiple accept="image/*" @change="onFileChanged" id="imageInput" type="file"/>
      <button @click="uploadImages">Submit</button>
    </div>
    <div>
      <input type="text" v-model="keyword" placeholder="Enter search keyword" />
      <input type="text" v-model="number" placeholder="Enter search number" />
      <button @click="searchImages">Search</button>
      <ul>
        <li v-for="(image, index) in images" :key="index">
          <img :src="'http://localhost:8000/media/'+image" />
        </li>
    </ul>
    </div>
    

  </div>
</template>

<script>
export default {
  data() {
    return {
      keyword: "",
      number: "",
      images: [],
      selectedImages: null,
    };
  },
  methods: {
    searchImages() {
      window.console.log("fetching");
      fetch('http://localhost:8000/api/search/?format=json&keyword=' + this.keyword + '&number=' + this.number)
        .then(response => {
          if (!response.ok) {
           throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          window.console.log(data);
          this.images = data.result;
        })
        .catch(error => {
          window.console.error('There was a problem with the fetch operation:', error);
          window.console.error(error);
        });
    },

    onFileChanged (event) {
      this.selectedImages = event.target.files
      window.console.log(this.selectedImages)

    },

    uploadImages() {
      let formData = new FormData();
      for(var i = 0; i < this.selectedImages.length; ++i){
        window.console.log(this.selectedImages[i])
        formData.append('file_list', this.selectedImages[i])
      }
      fetch('http://localhost:8000/api/upload/', {
        method : 'POST',
        body : formData
      }).then(response => {
        window.alert("upload success")
        return response.json();
      })
      .catch(error => {
        window.alert("upload fail")
        window.console.error('There was a problem with the upload operation:', error);
      });
    },


  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
hr {
  max-width: 65%;
}

.msg {
  margin: 0 auto;
  max-width: 30%;
  text-align: left;
  border-bottom: 1px solid #ccc;
  padding: 1rem;
}

.msg-index {
  color: #ccc;
  font-size: 0.8rem;
  /* margin-bottom: 0; */
}

img {
  width: 250px;
  padding-top: 50px;
  padding-bottom: 50px;
}

</style>
