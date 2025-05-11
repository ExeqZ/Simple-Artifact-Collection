const app = Vue.createApp({
  data() {
    return {
      files: [],
      connectionId: '', // Updated field name
      message: '',
      success: false,
    };
  },
  methods: {
    handleFileChange(event) {
      this.files = Array.from(event.target.files);
    },
    async uploadFiles() {
      if (this.files.length === 0) {
        this.message = 'Please select at least one file.';
        this.success = false;
        return;
      }

      const formData = new FormData();
      this.files.forEach(file => formData.append('file', file));
      formData.append('connectionId', this.connectionId);

      try {
        const response = await fetch('/manage/api/upload', {
          method: 'POST',
          body: formData,
        });

        const result = await response.json();
        if (response.ok) {
          this.message = `Files uploaded successfully to container: ${result.container_name}`;
          this.success = true;
        } else {
          this.message = `Error: ${result.error}`;
          this.success = false;
        }
      } catch (error) {
        console.error('Error uploading files:', error);
        this.message = 'An error occurred during file upload.';
        this.success = false;
      }
    },
  },
});

app.mount('#app');