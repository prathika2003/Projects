const state=["mumbai","delhi","kolkata","chennai"];
let index =state.indexOf("kolkata");
console.log(index);

const state1 = ["mumbai", "delhi", "kolkata", "chennai", "kolkata"];
let index1 = state1.indexOf("kolkata", 3);
console.log(index1);

const state2 = ["mumbai", "delhi", "kolkata", "chennai", "punjab", "banglore", "rajasthan"];
const slicedState1 = state2.slice(2);
const slicedState2 = state2.slice(-3);
console.log("original:", state2);
console.log("new:", slicedState1);
console.log("new:", slicedState2);

const myArray = [1, 2, 3, 4, 5];
for (let i = 0; i < myArray.length; i++) {
    console.log(myArray[i]);
}

const myArray1=[1, 2, 3, 4, 5];
for(const element of myArray){
    console.log(element);
}

const fruits=["apple","banana","orange"];
for(let index in fruits){
    console.log(fruits[index]);
}

const person={
    name: "john",
    age: 24,
    hobbies: ["reading","cooking"]
};
console.log(person.name);

let bikes = ["yamaha", "bajaj", "honda", "tvs"];
console.log(bikes.toString());

console.log(bikes.join());

console.log(bikes.pop());

console.log(bikes.push("royal enfeild"));
console.log(bikes);

console.log(bikes.shift());
console.log(bikes);

console.log(bikes.unshift("bmw", "kavasaki"));
console.log(bikes);
delete bikes[1];
console.log(bikes);

let arr1=[9, 2, 1];
let arr2=[10, 20, 30];
let arr_new=arr1.concat(arr2);
console.log(arr_new);
arr1.sort();
console.log(arr1);
arr2.splice(1);
console.log(arr2);

let numbers=[1, 2, 3, 4, 5, 6];
let num2=numbers.slice(1, 4);
console.log(num2);
numbers.reverse();
console.log(numbers);
console.log(Array.isArray(numbers));

let strng="hello";
console.log(Array.isArray(strng));

let bikes1 = ["yamaha", "bajaj", "honda", "tvs"];
console.log(bikes.indexOf("honda",0));

const Array2 = [5, 12, 8, 130, 44];
const found = Array2.find((element) => element > 10);
console.log(found);

const num3 = [1, 2, 3];
console.log(num3.includes(4));

const days=["sun", "mon", "tue", "wed", "thru", "fri", "sat"];
const day=days.entries();
for(let x of day){
    console.log(x + "\n");
}


const add = (a, b) => a + b;
console.log(add(3, 4)); 

function show() {
    console.log(this);
}
show(); 

const person1 = {
    name: "Bob",
    greet: () => {
        console.log("Hello, " + this.name);
    }
};

person1.greet(); 

function outer() {
    let count = 1;
    return function inner() {
        count++;
        console.log(count);
    };
}

const counter = outer(); // Closure is created
counter(); // Output: 1
counter(); // Output: 2
 


