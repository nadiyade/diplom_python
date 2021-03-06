from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views import ClientClaimCreateView, ClientClaimUpdateView, ClientClaimDeleteView, ClientClaimListView, \
    client_claims, ClaimApproveUpdateView, CommentCreateView, ClaimRejectUpdateView, ClaimRestoreUpdateView, \
    ClaimToRestoreListView, ClaimFinalRejectUpdateView, ClaimAllRejectedListView, ClaimInProgressListView, \
    ClaimWaitingListView

app_name = 'mydiplom'
urlpatterns = [
    path('claim/create/', ClientClaimCreateView.as_view(), name='claim_create'),
    path('claim/update/<int:pk>', ClientClaimUpdateView.as_view(), name='claim_update'),
    path('claim/delete/<int:pk>', ClientClaimDeleteView.as_view(), name='claim_delete'),
    path('claim/list/', ClientClaimListView.as_view(), name='client_claim_list'),  # by user in his cabinet
    path('claims/', client_claims, name='client_claims'),  # for admin
    path('claim/approve/<int:pk>', ClaimApproveUpdateView.as_view(), name='approve_claim'),  # by admin
    path('claim/reject/<int:pk>', ClaimRejectUpdateView.as_view(), name='reject_claim'),
    path('claim/finalreject/<int:pk>', ClaimFinalRejectUpdateView.as_view(), name='final_reject_claim'),
    path('claim/restore/<int:pk>', ClaimRestoreUpdateView.as_view(), name='restore_claim'),
    path('claim/torestore/', ClaimToRestoreListView.as_view(), name='claim_to_restore'),
    path('claim/allrejected/', ClaimAllRejectedListView.as_view(), name='all_rejected'),
    path('claim/inprogress/', ClaimInProgressListView.as_view(), name='in_progress'),
    path('claim/waiting/', ClaimWaitingListView.as_view(), name='claims_waiting'),
    path('claim/comment/', CommentCreateView.as_view(), name='comment_create'),  # by user
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
