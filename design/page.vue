<template>
  <div id="main">
    <div id="container">
      <div id="text">

        <form>
          <input type="file" ref="fileInput"/>
          <button type="button" @click="uploadFile()" style="margin-left:10px; margin-right:10px;">上传</button>
          <button type="reset"style="margin-left:15px; ">重置</button>
        </form>

        <form>
          <select v-model="query"  style="border-radius: 5px;width: 180px; height: 50px; margin-top: 20px;magin-left:3px;">
            <option value="" disabled selected hidden>要识别的图片</option>
            <option v-for="(item, index) in sortedFileList" :key="item.id" :value="item.name">{{ item.name }}</option>
          </select>
          <div style="display: inline-block; margin-left: 10px;">
            <select v-model="model" style="border-radius: 5px;width: 205px; height: 50px;">
              <option value="OCR" selected>OCR识别文字</option>
              <option value="Bert">Bert提取关键信息</option>
              <option value="LayoutXLM">LayoutXLM提取关键信息</option>
            </select>
          </div>
          <div style="display: inline-block; margin-left: 10px;">
            <select v-if="model === 'Bert'" v-model="invoiceType" style="border-radius: 5px;width: 130px; height: 50px;">
              <option value="" disabled selected hidden>要识别的发票类型</option>
              <option value="出院小结">出院小结</option>
              <option value="购药发票">购药发票</option>
              <option value="门诊发票">门诊发票</option>
              <option value="住院发票">住院发票</option>
            </select>
          </div>
          <br/>
          <button type="button" @click="sourcepic() " >原图</button>
          <button type="button" @click="recognition() " >识别</button>
          <button type="button" @click="sharpen()" >锐化</button>
          <button type="button" @click="smooth()" >平滑</button>
          <button type="button" @click="shadow()" style="margin-top: 10px;margin-right:2px;">去阴影</button>
          <br/>
          <div id="fileList" >
            <label class="label" style="font-size: 17px; color: #666;">文件列表(点击下载对应图片)</label>
            <ul style="list-style: none; margin: 0; padding: 0;">
              <li v-for="(item, index) in formData.fileList" :key="item.id" style="line-height: 30px;">
                <a href="#" @click="handleDownload(item.name)" style="color: #0366d6; text-decoration: none;">{{ item.name }}</a>
              </li>
            </ul>
          </div>
          <br/>

          <textarea v-model="message" rows="5" cols="43" class="transparent"placeholder="识别结果..." @focus="onFocus"></textarea>
          <br/>
          <input type="text" v-model="correct" style="width: 450px;height:50px;" placeholder="请输入纠错列表，以空格为间隔" @focus="onFocus">
          <button type="button" @click="error_correct() " style="margin-top: 10px; margin-bottom: 10px;margin-left:20px;">纠错</button>
          <br/>
          <textarea v-model="correct_message" rows="3" cols="43"placeholder="纠错结果..." @focus="onFocus"></textarea>
          <img :src="imageData" style="position: absolute; left: 650px; top: 20px;" />
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import 'axios/dist/axios.min.js'
import Vue from 'vue';

Vue.prototype.$axios = axios;
export default {
  name: 'test',
  data() {
    return {
      formData: {
        fileList: [],
      },
      selectedFile: "",
      sortedFileList: [],
      message: "",
      query: "",
      file: null,
      imageData: null,
      model: "OCR",    // 默认选择 OCR 模式
      invoiceType: "", // 发票类型
      correct:"",
      correct_message:'',
    }
  },
  created() {
    this.getFiles();
  },
  methods: {
    onFocus() {
      this.$refs.myInput.placeholder = ''
    },
    getFiles() {
      axios.get('http://127.0.0.1:80/get_files')
        .then(response => {
          this.formData.fileList = response.data["files"];
          this.sortedFileList = response.data["files"].sort((a, b) => a.name.localeCompare(b.name));
        });
    },
    handleDownload(filename) {
      // 下载对应的文件
      window.location.href = 'http://127.0.0.1:80/download?filename=' + filename;
    },
    handleSelectChange() {
      this.query = this.selectedFile;
    },
    uploadFile() {
      const fileInput = this.$refs.fileInput;
      const file = fileInput.files[0];
      const formData = new FormData();
      formData.append('filename', file);

      axios.post('http://127.0.0.1:80/file_rec', formData)
        .then(response => {
          console.log(response.data);
          this.query = response.data["fileName"];
          this.getFiles(); // 上传成功后立即更新文件列表视图
        })
        .catch(e => {
          console.log(e.response.data.message);
        });
    },
    recognition() {
      let backendUrl;
      if (this.model === 'OCR') {
        backendUrl = 'http://127.0.0.1:90/recognition';
      } else if (this.model === 'Bert') {
        backendUrl = 'http://127.0.0.1:81/NER';
      } else {
        backendUrl = 'http://127.0.0.1:82/SER';
      }
      this.$axios.get(backendUrl, { params: { "message":this.message,"query": this.query,"invoiceType":this.invoiceType } })
        .then(response => {
          console.log(this.message);
          console.log(response.data);
          if ("image_data" in response.data) {
            this.message = response.data["result"];
            const img = new Image();
            img.onload = () => {
              let width = 1200;
              let height = 800;
              if (img.width > width || img.height > height) {
                const scale = Math.min(width / img.width, height / img.height);
                width = Math.round(img.width * scale);
                height = Math.round(img.height * scale);
              }
              const canvas = document.createElement("canvas");
              canvas.width = width;
              canvas.height = height;
              const ctx = canvas.getContext("2d");
              ctx.drawImage(img, 0, 0, width, height);
              this.imageData = canvas.toDataURL();
            };
            img.src = 'data:image/jpeg;base64,' + response.data.image_data;

          } else {
            this.message = response.data["result"];
          }
        })
    },
    sourcepic(){
      this.$axios
        .get("http://127.0.0.1:90/sourcepic", { params: { query: this.query } }, { responseType: "blob" })
        .then((response) => {
          const img = new Image();
          img.onload = () => {
            let width = 1200;
            let height = 800;
            if (img.width > width || img.height > height) {
              const scale = Math.min(width / img.width, height / img.height);
              width = Math.round(img.width * scale);
              height = Math.round(img.height * scale);
            }
            const canvas = document.createElement("canvas");
            canvas.width = width;
            canvas.height = height;
            const ctx = canvas.getContext("2d");
            ctx.drawImage(img, 0, 0, width, height);
            this.imageData = canvas.toDataURL();
          };
          img.src = 'data:image/jpeg;base64,' + response.data.image_data;
        })
        .catch((error) => {
          console.error(error);
        });
    },
    sharpen() {
      this.$axios
        .get("http://127.0.0.1:90/sharpen", { params: { query: this.query } }, { responseType: "blob" })
        .then((response) => {
          const img = new Image();
          img.onload = () => {
            let width = 1200;
            let height = 800;
            if (img.width > width || img.height > height) {
              const scale = Math.min(width / img.width, height / img.height);
              width = Math.round(img.width * scale);
              height = Math.round(img.height * scale);
            }
            const canvas = document.createElement("canvas");
            canvas.width = width;
            canvas.height = height;
            const ctx = canvas.getContext("2d");
            ctx.drawImage(img, 0, 0, width, height);
            this.imageData = canvas.toDataURL();
          };
          img.src = 'data:image/jpeg;base64,' + response.data.image_data;
        })
        .catch((error) => {
          console.error(error);
        });
    },

    smooth() {
      this.$axios
        .get("http://127.0.0.1:90/smooth", { params: { query: this.query } }, { responseType: "blob" })
        .then((response) => {
          const img = new Image();
          img.onload = () => {
            let width = 1200;
            let height = 800;
            if (img.width > width || img.height > height) {
              const scale = Math.min(width / img.width, height / img.height);
              width = Math.round(img.width * scale);
              height = Math.round(img.height * scale);
            }
            const canvas = document.createElement("canvas");
            canvas.width = width;
            canvas.height = height;
            const ctx = canvas.getContext("2d");
            ctx.drawImage(img, 0, 0, width, height);
            this.imageData = canvas.toDataURL();
          };
          img.src = 'data:image/jpeg;base64,' + response.data.image_data;
        })
        .catch((error) => {
          console.error(error);
        });
    },
    shadow(){
      this.$axios
        .get("http://127.0.0.1:84/shadow", { params: { query: this.query } }, { responseType: "blob" })
        .then((response) => {
          const img = new Image();
          img.onload = () => {
            let width = 1200;
            let height = 800;
            if (img.width > width || img.height > height) {
              const scale = Math.min(width / img.width, height / img.height);
              width = Math.round(img.width * scale);
              height = Math.round(img.height * scale);
            }
            const canvas = document.createElement("canvas");
            canvas.width = width;
            canvas.height = height;
            const ctx = canvas.getContext("2d");
            ctx.drawImage(img, 0, 0, width, height);
            this.imageData = canvas.toDataURL();
          };
          img.src = 'data:image/jpeg;base64,' + response.data.image_data;
        })
        .catch((error) => {
          console.error(error);
        });
    },
    error_correct(){
      this.$axios
        .get("http://127.0.0.1:83/error_correct", {params: {message: this.message,correct:this.correct}})
        .then((response) => {
          console.log(response.data);
          this.correct_message = response.data["result"];
          this.message = response.data["message"];
        })
        .catch((error) => {
          console.error(error);
        });
    },
  }
}

</script>

<style scoped>
#main {
  width: 100%;
  min-height: 100vh;
  position: absolute;
  background-size: 100% 100%;
}
#container {
  width: 100%;
  position: relative;
  height: 1000px;
  overflow: auto;
}
#text {
  font-family:NSimSun;

  background-image: url("https://ts1.cn.mm.bing.net/th/id/R-C.5d82907b7ba355af8b8e24529d1b2d07?rik=wHhHg8RgTAE7wQ&riu=http%3a%2f%2fimg.pptjia.com%2fimage%2f20190116%2fbedf099163ccc9295bdecbacb2b4f0bf.jpg&ehk=DHP6Xhxkj6ZhsTf4lXy4c1PuL5W7p%2fMN1P0dHj8Vs5o%3d&risl=&pid=ImgRaw&r=0");
  background-repeat: no-repeat; /* 图片不重复 */
  background-size: 100% auto;
  width: 100%;
  height: 1000px;
  font-size:24px;
  margin-top:10px;
  padding: 20px;
  box-shadow: #cc0000;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border: 2px solid #ccc;
}
input{
  width:375px;
  background-color: rgba(240, 255, 240, 0.5);
  border-radius: 10px;
  box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3); /* 添加阴影效果 */
  transition: all 0.3s ease-in-out; /* 添加动画效果 */
}
input:hover {
  background-color: rgba(200, 250, 200, 0.7); /* 鼠标滑过时改变背景颜色 */
  box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.5); /* 添加更明显的阴影效果 */
}
select{
  font-size:18px;
  background-color: rgba(240, 255, 240, 0.5);
  border-radius: 10px;
  box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3); /* 添加阴影效果 */
  transition: all 0.3s ease-in-out; /* 添加动画效果 */

}
select:hover {
  background-color: rgba(200, 250, 200, 0.7); /* 鼠标滑过时改变背景颜色 */
  box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.5); /* 添加更明显的阴影效果 */
}
button {
  font-family:Arial;
  font-size:20px;
  font-weight:500;
  margin-right: 50px;
  margin-top: 5px;
  background-color: rgba(240, 255, 240, 0.5);
  border-radius: 10px;
  box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3); /* 添加阴影效果 */
  transition: all 0.3s ease-in-out; /* 添加动画效果 */
  padding:10px;
}
button:hover {
  background-color: rgba(200, 250, 200, 0.7); /* 鼠标滑过时改变背景颜色 */
  box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.5); /* 添加更明显的阴影效果 */
}

file:hover {
  background-color: rgba(255, 255, 255, 0.7); /* 鼠标滑过时改变背景颜色 */
  box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.5); /* 添加更明显的阴影效果 */
}
#fileList {

  margin-top: 30px;
  width: 535px;
  font-size:20px;
  overflow-y: auto;
  height: 200px;
  overflow-y: auto;
  padding: 10px;
  background-color: rgba(235, 250, 235, 0.3);
  border: 2px solid #ccd0d5;
  border-radius: 5px;
}

textarea {
  border-radius: 5px;
  background-color: rgba(235, 250, 235, 0.4);

}
textarea:hover {
  background-color: rgba(200, 250, 200, 0.7); /* 鼠标滑过时改变背景颜色 */
  box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.5); /* 添加更明显的阴影效果 */
}
</style>