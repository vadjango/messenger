export const numToMonth = ["січня",
                           "лютого", 
                           "березня", 
                           "квітня", 
                           "травня", 
                           "червня", 
                           "липня", 
                           "серпня", 
                           "вересня", 
                           "жовтня",
                           "листопада",
                           "грудня"];

export const toReadableTime = (dateTime: Date): string => {
    return `${dateTime.getHours().toString().padStart(2, "0")}:${dateTime.getMinutes().toString().padStart(2, "0")}`
}

export const toReadableDate = (dateTime: Date): string => {
    return `${dateTime.getDate()} ${numToMonth[dateTime.getMonth()]}`
}

export const toReadableDateTime = (dateTime: Date): string => {
    return `${dateTime.getDate().toString().padStart(2, "0")}.${(dateTime.getMonth() + 1).toString().padStart(2, "0")}.${dateTime.getFullYear()} ${toReadableTime(dateTime)}`
}