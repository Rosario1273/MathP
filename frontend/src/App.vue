<template>
  <div id="app">
    <h1 class="title">Transportation Problem Solver</h1>

    
    <div v-if="!selectedMethod" class="method-selection">
      <h2>Select a Method</h2>
      <button class="method-button" @click="selectMethod('north-west')">
        North-West Corner Method
      </button>
      <button class="method-button" @click="selectMethod('least-cost')">
        Least Cost Method
      </button>
      <button class="method-button" @click="selectMethod('vogel')">
        Vogel's Approximation Method
      </button>
    </div>

    
    <div v-if="selectedMethod">
      <h2>Enter Data for {{ selectedMethodName }}</h2>
      <div>
        <label for="supply">Supply:</label>
        <input type="text" v-model="supplyInput"  @input="updateTable" />
      </div>
      <div>
        <label for="demand">Demand:</label>
        <input type="text" v-model="demandInput"  @input="updateTable" />
      </div>
      <div>
        <label for="costs">Cost Matrix:</label>
        <input type="text" v-model="costInput" @input="updateTable"    />
      </div>

      <div>
        <h3>Cost Table and Allocations</h3>
        <table class="transportation-table">
          <thead>
            <tr>
              <th>Source/Destination</th>
              <th v-for="index in (parsedDemand.length || 3)" :key="'header-' + index">
                {{ parsedDemand.length ? 'D' + index : 'D' + index }}
              </th>
              <th>Supply</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="rowIndex in (parsedSupply.length || 3)" :key="'row-' + rowIndex">
              <td><strong>S{{ rowIndex }}</strong></td>
              <td v-for="colIndex in (parsedDemand.length || 3)" :key="'cell-' + rowIndex + '' + colIndex">
                <div v-if="costMatrix.length && costMatrix[rowIndex - 1]?.[colIndex - 1] !== undefined">
                  {{ costMatrix[rowIndex - 1][colIndex - 1] }}
                </div>
                <div v-if="allocationMatrix.length && allocationMatrix[rowIndex - 1]?.[colIndex - 1] > 0">
                  <strong>{{ allocationMatrix[rowIndex - 1][colIndex - 1] }}</strong>
                </div>
                <div v-else></div>
              </td>
              <td>{{ parsedSupply[rowIndex - 1] || '' }}</td>
            </tr>
          </tbody>
          <tfoot>
            <tr>
              <td>Demand</td>
              <td v-for="index in (parsedDemand.length || 3)" :key="'footer-demand-' + index">
                {{ parsedDemand[index - 1] || '' }}
              </td>
              <td>{{ totalSupply || '' }}</td>
            </tr>
          </tfoot>
        </table>
      </div>

      <button class="managing-button" @click="solve">Solve</button>
      <button class="managing-button" @click="resetInput">Reset Input</button>
      <button class="managing-button" @click="goBack">Back</button>
    </div>

    <div v-if="solution" class="solution">
      <h2>Solution</h2>
      <p class="total-cost">Total Cost: {{ totalCost }}</p>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      selectedMethod: null,
      selectedMethodName: "",
      supplyInput: "",
      demandInput: "",
      costInput: "",
      costMatrix: [],
      allocationMatrix: [],
      solution: null,
      totalCost: 0,
      highlightedCells: [],
    };
  },
  computed: {
  parsedSupply() {
    const result = this.supplyInput
      .split(",")
      .map((value) => Number(value.trim()))
      .filter((n) => !isNaN(n) && n >= 0); 
    console.log("Parsed Supply:", result);
    return result;
  },
  parsedDemand() {
    const result = this.demandInput
      .split(",")
      .map((value) => Number(value.trim()))
      .filter((n) => !isNaN(n) && n >= 0); 
    console.log("Parsed Demand:", result);
    return result;
  },
  totalSupply() {
    const total = this.parsedSupply.reduce((a, b) => a + b, 0);
    console.log("Total Supply:", total);
    return total;
  },
  totalDemand() {
    const total = this.parsedDemand.reduce((a, b) => a + b, 0);
    console.log("Total Demand:", total);
    return total;
  },
},
  methods: {
    selectMethod(method) {
      this.selectedMethod = method;
      this.selectedMethodName = method.replace("-", " ").toUpperCase();
      this.resetInput();
    },
    updateTable() {
      this.costMatrix = this.parseCostInput();
      this.allocationMatrix = Array(this.parsedSupply.length)
        .fill(0)
        .map(() => Array(this.parsedDemand.length).fill(0));
    },
    parseCostInput() {
      if (!this.costInput) return [];
      return this.costInput.split(";").map((row) =>
        row.split(",").map(Number)
      );
    },
    resetInput() {
      this.supplyInput = "";
      this.demandInput = "";
      this.costInput = "";
      this.costMatrix = [];
      this.allocationMatrix = [];
      this.solution = null;
      this.totalCost = 0;
      this.highlightedCells = [];
    },
    async solve() {
      console.log("Start log");
      console.log("Parsed Supply:", this.parsedSupply);
      console.log("Parsed Demand:", this.parsedDemand);
      console.log("Total Supply:", this.totalSupply);
      console.log("Total Demand:", this.totalDemand);
      console.log("Total Supply lenght:", this.parsedSupply.length);
      console.log("Total Demand lenght:", this.parsedDemand.length);

      
      if (this.totalSupply === 0 || this.totalDemand === 0) {
       alert("Supply and demand must have at least a value of 1");
       return;
}
      if (this.totalSupply !== this.totalDemand) {
        alert("The total supply must equal the total demand.");
        return;
      }


      const expectedCostElements = this.parsedSupply.length * this.parsedDemand.length;
      const actualCostElements = this.costMatrix.flat().length;
      
      if (actualCostElements !== expectedCostElements) {
        alert(
          `The cost matrix must have exactly ${expectedCostElements} elements, but it has ${actualCostElements}.`
        );
        return;
      }

      const payload = {
        method: this.selectedMethod,
        supply: this.parsedSupply,
        demand: this.parsedDemand,
        costs: this.costMatrix,
      };

      try {
        const response = await axios.post("http://localhost:5000/solve", payload);
        const { allocation, totalCost, highlightedCells } = response.data;

        this.allocationMatrix = allocation;
        this.totalCost = totalCost;
        this.highlightedCells = highlightedCells;
        this.solution = true;
      } catch (error) {
        console.error("Error solving transportation problem:", error);
        alert("There was an error solving the problem. Please check your input or try again.");
      }
    },
    goBack() {
      this.selectedMethod = null;
      this.resetInput();
    },
  },
};
</script>

<style>
body {
  font-family: Arial, sans-serif;
  background-color: #000000; 
  color: #e0e0e0; 
  margin: 0;
  padding: 0;
}


.total-cost {
  color: #ffffff; 
  font-weight: bold; 
  font-size: 22px; 
}

.title {
  text-align: center;
  color: #4cafef; 
}


.method-button,
.managing-button {
  background-color: #4cafef;
  color: #000000;
  border: none;
  padding: 10px 20px;
  margin: 10px;
  font-size: 16px;
  cursor: pointer;
  border-radius: 5px;
  transition: background-color 0.3s ease;
}



label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

input[type="text"] {
  width: 50%;
  padding: 10px;
  border: 1px solid #4cafef;
  border-radius: 5px;
  background-color: #000000;
  color: #e0e0e0;
  outline: none;
}


.transportation-table {
  border-collapse: collapse;
  width: 100%;
  margin-top: 20px;
  background-color: #000000;
  color: #e0e0e0;
}

.transportation-table th,
.transportation-table td {
  border: 1px solid #4cafef;
  padding: 10px;
  text-align: center;
}

.transportation-table th {
  background-color: #4cafef;
  color: #000000;
}

.solution {
  margin-top: 20px;
  color:  #4cafef;
  text-align: center;
}
</style>
