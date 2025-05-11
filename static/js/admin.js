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
        this.cases = Array.from(caseElements).map((el) => el.innerText);
      } catch (error) {
        console.error('Error fetching cases:', error);
      }
    },
    async createCase() {
      if (!this.newCaseName) {
        this.message = 'Case name is required.';
        return;
      }

      try {
        const response = await fetch('/admin', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams({ case_name: this.newCaseName }),
        });

        if (response.ok) {
          this.message = 'Case created successfully!';
          this.newCaseName = '';
          await this.fetchCases();
        } else {
          this.message = 'Error creating case.';
        }
      } catch (error) {
        console.error('Error creating case:', error);
        this.message = 'Error creating case.';
      }
    },
  },
});

adminApp.mount('#app');