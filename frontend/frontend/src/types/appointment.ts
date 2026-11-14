export type AppointmentStatus = "pending" | "confirmed" | "completed" | "canceled"

export interface Appointment {
 id: string;
 client_id: string;
 provider_id: string;
 service_id: string;
 business_id: string;
 appointment_start: string;
 end_time: string;
 status: string;
 statys: AppointmentStatus
 notes: string | null

}