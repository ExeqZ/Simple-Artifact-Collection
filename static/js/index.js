const app = Vue.createApp({
  data() {
    return {
      files: [],
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

      try {
        const response = await fetch('/upload', {
          method: 'POST',
          body: formData,
        });

        const result = await response.text();
        if (response.ok) {
          this.message = `Success: ${result}`;
          this.success = true;
        } else {
          this.message = `Error: ${result}`;
          this.success = false;
        }
      } catch (error) {
        this.message = `Error: ${error.message}`;
        this.success = false;
      }
    },
  },
});

app.mount('#app');