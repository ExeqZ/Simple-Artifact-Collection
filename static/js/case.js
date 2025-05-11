const caseApp = Vue.createApp({
  data() {
    return {
      blobs: [],
    };
  },
  async mounted() {
    await this.fetchBlobs();
  },
  methods: {
    async fetchBlobs() {
      try {
        const response = await fetch(window.location.href);
        const html = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const blobElements = doc.querySelectorAll('.file-list > li');
        this.blobs = Array.from(blobElements).map((el) => el.innerText);
      } catch (error) {
        console.error('Error fetching blobs:', error);
      }
    },
  },
});

caseApp.mount('#app');