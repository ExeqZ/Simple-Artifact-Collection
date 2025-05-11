const app = Vue.createApp({
  data() {
    return {
      files: [],
    };
  },
  async mounted() {
    await this.fetchFiles();
  },
  methods: {
    async fetchFiles() {
      try {
        const response = await fetch('/manage');
        this.files = await response.json();
      } catch (error) {
        console.error('Error fetching files:', error);
      }
    },
    async deleteFile(fileName) {
      try {
        const response = await fetch('/manage', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ file_to_delete: fileName }),
        });

        if (response.ok) {
          this.files = this.files.filter(file => file.name !== fileName);
        } else {
          console.error('Error deleting file:', await response.text());
        }
      } catch (error) {
        console.error('Error deleting file:', error);
      }
    },
  },
});

app.mount('#app');