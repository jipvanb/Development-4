let changes = 0;
let reserveButton = document.getElementById('reserve')
let reserveButton2 = document.getElementById('reserve2')
reserveButton.addEventListener('click', () => {
    document.getElementById('returnDiv').style.display = 'block'
    if(changes > 0){
        
    }
})
{
function checkIfChanged(){

}
start = document.getElementById('start')

start.addEventListener('change', (event) => {
    function addDays(date, days) {
        var result = new Date(date);
        result.setDate(result.getDate() + days);
        return result;
      }
    
    let startLabel = document.getElementById('startLabel')
    let checks = document.querySelector('.checks')
   
    checks.style.transform = 'translate(0,-100%)'
    reserveButton.style.display = 'none'
    reserveButton2.style.display = 'block'
    
    changes++
    let newDate = document.getElementById('start').value
    
    document.getElementById('currentDay').textContent = `Current start date is: ${newDate}`
    console.log(newDate)
    
    let today = new Date().toLocaleDateString('en-ca')
    let tomorrow = addDays(newDate, 1)
    let array = tomorrow.toString().split(' ')
    function month(word) {
        let months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        let int;
        months.forEach((month) => {
            if(month === word){
                int = months.indexOf(word)
               int = int + 1
               int = `0${int}`
               console.log(int, "yea")
               return int
            }
        })
        console.log(int)
        return int
    }
    console.log(array, "array")
    let monthIntstart = month(array[1])
    let startDate = `${array[0]}${array[3]}-${monthIntstart}-${array[2]}`
   
  
    console.log(startDate)
   
})
}