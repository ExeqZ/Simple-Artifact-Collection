const adminApp = Vue.createApp({
  data() {
    return {
      cases: [],
      newCaseName: '',
      message: '',
    };
  },
  async mounted() {
    await this.fetchCases();
  },
  methods: {
    async fetchCases() {
      try {
        const response = await fetch('/admin');
        const html = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const caseElements = doc.querySelectorAll('ul > li');
        this.cases = Array.from(caseElements).map(el => el.innerText);
      } catch (error) {
        console.error('Error fetching cases:', error);
      }
    },
    async createCase() {
      if (!this.newCaseName) {
        this.message = 'Please enter a case name.';
        return;
      }

      const connectionId = this.generateConnectionId(); // Generate connection ID
      const formData = new FormData();
      formData.append('case_name', this.newCaseName);
      formData.append('connection_id', connectionId);

      try {
        const response = await fetch('/admin', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          this.message = 'Case created successfully!';
          this.newCaseName = '';
          await this.fetchCases(); // Refresh the case list
        } else {
          this.message = 'Error creating case.';
        }
      } catch (error) {
        console.error('Error creating case:', error);
        this.message = 'Error creating case.';
      }
    },
    generateConnectionId() {
      // Generate a random connection ID in the format XXXX-XXXX-XXXX-XXXX
      return Array(4)
        .fill(0)
        .map(() => Math.random().toString(36).substring(2, 6).toUpperCase())
        .join('-');
    },
  },
});

adminApp.mount('#app');