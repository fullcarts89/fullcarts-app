"use server";

import { revalidatePath } from "next/cache";
import { createAdminClient } from "@/lib/supabase/admin";

export async function setEntityRetracted(entityId: string, retracted: boolean) {
  const supabase = createAdminClient();

  const { data, error } = await supabase.rpc("set_entity_retracted", {
    p_entity_id: entityId,
    p_retracted: retracted,
  });

  if (error) {
    throw new Error(`Failed to ${retracted ? "retract" : "restore"} entity: ${error.message}`);
  }

  revalidatePath("/admin/entities");

  const eventsAffected = (data as Array<{ events_affected: number }> | null)?.[0]?.events_affected ?? 0;
  return { eventsAffected };
}
