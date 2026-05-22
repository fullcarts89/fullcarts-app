import { NextRequest, NextResponse } from "next/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { isAdminRequest } from "@/lib/admin-auth";

// POST /api/admin/reassign-events-by-size
//
// Body (one of):
//   { sourceEntityId, sizeBefore, sizeAfter, sizeUnit, targetEntityId }
//   { sourceEntityId, sizeBefore, sizeAfter, sizeUnit,
//     newEntityBrand, newEntityName, newEntityCategory? }
//
// In the second form we create the target entity first, then call the
// reassign_events_by_size RPC. Both forms are all-or-nothing — if the
// RPC errors, the (just-created) entity stays around as an orphan, which
// is acceptable since the admin can retract it from /admin/entities.
//
// Returns: { targetEntityId, eventsMoved, claimsMoved }

export const dynamic = "force-dynamic";

interface ExistingTargetBody {
  sourceEntityId: string;
  sizeBefore: number;
  sizeAfter: number;
  sizeUnit: string;
  targetEntityId: string;
}

interface NewTargetBody {
  sourceEntityId: string;
  sizeBefore: number;
  sizeAfter: number;
  sizeUnit: string;
  newEntityBrand: string;
  newEntityName: string;
  newEntityCategory?: string | null;
}

type Body = ExistingTargetBody | NewTargetBody;

function isExisting(b: Body): b is ExistingTargetBody {
  return typeof (b as ExistingTargetBody).targetEntityId === "string";
}

export async function POST(request: NextRequest) {
  if (!(await isAdminRequest())) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const raw = await request.json().catch(() => null);
  if (!raw || typeof raw !== "object") {
    return NextResponse.json({ error: "Invalid body" }, { status: 400 });
  }
  const b = raw as Partial<Body>;

  if (
    typeof b.sourceEntityId !== "string" ||
    typeof b.sizeBefore !== "number" ||
    typeof b.sizeAfter !== "number" ||
    typeof b.sizeUnit !== "string"
  ) {
    return NextResponse.json(
      { error: "sourceEntityId, sizeBefore, sizeAfter, sizeUnit required" },
      { status: 400 },
    );
  }

  const body = b as Body;
  const sb = createAdminClient();
  let targetEntityId: string;

  if (isExisting(body)) {
    targetEntityId = body.targetEntityId;
    if (targetEntityId === body.sourceEntityId) {
      return NextResponse.json(
        { error: "source and target must differ" },
        { status: 400 },
      );
    }
  } else {
    const brand = (body.newEntityBrand || "").trim();
    const name = (body.newEntityName || "").trim();
    if (!brand || !name) {
      return NextResponse.json(
        { error: "newEntityBrand and newEntityName required" },
        { status: 400 },
      );
    }
    const { data, error } = await sb
      .from("product_entities")
      .insert({
        brand,
        canonical_name: name,
        category: body.newEntityCategory ?? null,
      })
      .select("id")
      .single();
    if (error || !data) {
      return NextResponse.json(
        { error: `create entity failed: ${error?.message ?? "unknown"}` },
        { status: 500 },
      );
    }
    targetEntityId = data.id as string;
  }

  const { data: rpcData, error: rpcError } = await sb.rpc(
    "reassign_events_by_size",
    {
      p_source_entity_id: body.sourceEntityId,
      p_target_entity_id: targetEntityId,
      p_size_before: body.sizeBefore,
      p_size_after: body.sizeAfter,
      p_size_unit: body.sizeUnit,
      p_reassigned_by: "duplicates_extract",
    },
  );
  if (rpcError) {
    return NextResponse.json(
      { error: `reassign_events_by_size failed: ${rpcError.message}` },
      { status: 500 },
    );
  }
  const row = (
    rpcData as Array<{ events_moved: number; claims_moved: number }>
  )[0];

  return NextResponse.json({
    targetEntityId,
    eventsMoved: row?.events_moved ?? 0,
    claimsMoved: row?.claims_moved ?? 0,
  });
}
